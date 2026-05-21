"""
Trailer load planner for fixed-orientation crates.

Coordinate system (shown on the plot):
  - x = 0: rear doors (loading end)
  - x = length: cab end (toward the tractor / driver)
  - y = 0: left side, y = width: right side (viewed from the rear, facing the cab)

Crates are never rotated. Left/right balance and weight toward the cab are enforced.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Maximum allowed |left - right| / total loaded weight
BALANCE_TOLERANCE = 0.10

# Standard UK trailer (testing / default prompts)
UK_TRAILER_LENGTH_CM = 1360
UK_TRAILER_WIDTH_CM = 240
UK_TRAILER_HEIGHT_CM = 270
UK_TRAILER_MAX_WEIGHT_KG = 26000

@dataclass(frozen=True)
class TrailerSpec:
    name: str
    length_cm: float
    width_cm: float
    height_cm: float
    max_weight_kg: float


@dataclass(frozen=True)
class Crate:
    asset_tag: str
    length_cm: int
    width_cm: int
    height_cm: int
    weight_kg: float


@dataclass
class Placement:
    asset_tag: str
    x: int
    y: int
    length_cm: int
    width_cm: int


@dataclass
class LoadResult:
    trailer: TrailerSpec
    placements: list[Placement] = field(default_factory=list)
    overflow: list[str] = field(default_factory=list)
    skipped_too_tall: list[str] = field(default_factory=list)
    left_weight_kg: float = 0.0
    right_weight_kg: float = 0.0
    cab_weight_kg: float = 0.0
    door_weight_kg: float = 0.0

    @property
    def loaded_count(self) -> int:
        return len(self.placements)

    @property
    def total_weight_kg(self) -> float:
        return self.left_weight_kg + self.right_weight_kg


def _parse_size_string(size: str) -> tuple[float, float, float]:
    parts = str(size).lower().replace(" ", "").split("x")
    if len(parts) != 3:
        raise ValueError(f"Size must be three dimensions separated by 'x', got: {size!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def load_crates_from_excel(path: str | Path) -> list[Crate]:
    df = pd.read_excel(path)
    df["Asset Tag"] = df["Asset Tag"].astype(str)

    if {"Length (cm)", "Width (cm)", "Height (cm)"}.issubset(df.columns):
        lengths = df["Length (cm)"].astype(float)
        widths = df["Width (cm)"].astype(float)
        heights = df["Height (cm)"].astype(float)
    elif "Size (cm)" in df.columns:
        parsed = df["Size (cm)"].map(_parse_size_string)
        lengths = parsed.map(lambda t: t[0]) # type: ignore
        widths = parsed.map(lambda t: t[1]) # type: ignore
        heights = parsed.map(lambda t: t[2]) # type: ignore
    else:
        raise ValueError(
            "Excel must have either 'Length/Width/Height (cm)' columns "
            "or a 'Size (cm)' column (format: length x width x height)."
        )

    crates: list[Crate] = []
    for i, row in df.iterrows():
        crates.append(
            Crate(
                asset_tag=str(row["Asset Tag"]),
                length_cm=int(ceil(lengths.iloc[i])), # type: ignore
                width_cm=int(ceil(widths.iloc[i])), # type: ignore
                height_cm=int(ceil(heights.iloc[i])), # type: ignore
                weight_kg=float(row["Gross Weight (kg)"]),
            )
        )
    return crates


def _balance_ratio(left: float, right: float) -> float:
    total = left + right
    if total <= 0:
        return 0.0
    return abs(left - right) / total


class TrailerLoadPlanner:
    def __init__(self, trailer: TrailerSpec, balance_tolerance: float = BALANCE_TOLERANCE):
        self.trailer = trailer
        self.balance_tolerance = balance_tolerance
        self.grid_l = int(ceil(trailer.length_cm))
        self.grid_w = int(ceil(trailer.width_cm))
        self.grid = np.zeros((self.grid_l, self.grid_w), dtype=bool)
        self.placements: list[Placement] = []
        self.left_weight = 0.0
        self.right_weight = 0.0
        self.cab_weight = 0.0
        self.door_weight = 0.0
        self.loaded_weight = 0.0

    def _region_free(self, x: int, y: int, length: int, width: int) -> bool:
        if x < 0 or y < 0:
            return False
        if x + length > self.grid_l or y + width > self.grid_w:
            return False
        return not np.any(self.grid[x : x + length, y : y + width])

    def _weight_ok(self, added: float) -> bool:
        return self.loaded_weight + added <= self.trailer.max_weight_kg

    def _projected_balance_ok(self, weight: float, center_y: float) -> bool:
        new_left = self.left_weight + (weight if center_y < self.trailer.width_cm / 2 else 0)
        new_right = self.right_weight + (weight if center_y >= self.trailer.width_cm / 2 else 0)
        return _balance_ratio(new_left, new_right) <= self.balance_tolerance

    def _record_weight(self, weight: float, x: int, length: int, y: int, width: int) -> None:
        center_y = y + width / 2
        center_x = x + length / 2
        if center_y < self.trailer.width_cm / 2:
            self.left_weight += weight
        else:
            self.right_weight += weight
        if center_x > self.trailer.length_cm / 2:
            self.cab_weight += weight
        else:
            self.door_weight += weight
        self.loaded_weight += weight

    def _mark(self, x: int, y: int, length: int, width: int, crate: Crate) -> None:
        self.grid[x : x + length, y : y + width] = True
        self.placements.append(
            Placement(crate.asset_tag, x, y, length, width)
        )
        self._record_weight(crate.weight_kg, x, length, y, width)

    def _score_position(self, weight: float, x: int, length: int) -> float:
        """Higher is better. Heavy crates must sit toward the cab (high x), not the doors."""
        center_x = x + length / 2
        half = self.trailer.length_cm / 2
        if center_x <= half:
            return -weight * 5.0
        cab_frac = (center_x - half) / max(half, 1)
        return weight * (cab_frac**2) + center_x * 0.05

    def _score_pair(self, c1: Crate, c2: Crate, x: int, row_length: int) -> float:
        balance_bonus = 1.0 / (1.0 + abs(c1.weight_kg - c2.weight_kg))
        cab_bias = self._score_position(c1.weight_kg + c2.weight_kg, x, row_length)
        return cab_bias + balance_bonus * 100

    def _pair_fits(self, c1: Crate, c2: Crate, x: int) -> bool:
        y_left, y_right = 0, self.grid_w - c2.width_cm
        if not self._region_free(x, y_left, c1.length_cm, c1.width_cm):
            return False
        if not self._region_free(x, y_right, c2.length_cm, c2.width_cm):
            return False
        new_left = self.left_weight + c1.weight_kg
        new_right = self.right_weight + c2.weight_kg
        return _balance_ratio(new_left, new_right) <= self.balance_tolerance

    def _single_fits(self, crate: Crate, x: int, y: int) -> bool:
        if not self._region_free(x, y, crate.length_cm, crate.width_cm):
            return False
        center_y = y + crate.width_cm / 2
        return self._projected_balance_ok(crate.weight_kg, center_y)

    def _find_best_pair(self, remaining: list[Crate]) -> tuple[Crate, Crate, int] | None:
        best: tuple[float, Crate, Crate, int] | None = None
        for i, c1 in enumerate(remaining):
            for c2 in remaining[i + 1 :]:
                if c1.width_cm + c2.width_cm > self.grid_w:
                    continue
                if c1.height_cm > self.trailer.height_cm or c2.height_cm > self.trailer.height_cm:
                    continue
                if not self._weight_ok(c1.weight_kg + c2.weight_kg):
                    continue
                row_length = max(c1.length_cm, c2.length_cm)
                for x in range(self.grid_l - row_length, -1, -1):
                    if not self._pair_fits(c1, c2, x):
                        continue
                    score = self._score_pair(c1, c2, x, row_length)
                    if best is None or score > best[0]:
                        best = (score, c1, c2, x)
        if best is None:
            return None
        _, c1, c2, x = best
        return c1, c2, x

    def _find_best_single(self, remaining: list[Crate]) -> tuple[Crate, int, int] | None:
        best: tuple[float, Crate, int, int] | None = None
        for crate in remaining:
            if crate.height_cm > self.trailer.height_cm or not self._weight_ok(crate.weight_kg):
                continue
            for x in range(self.grid_l - crate.length_cm, -1, -1):
                for y in range(0, self.grid_w - crate.width_cm + 1):
                    if not self._single_fits(crate, x, y):
                        continue
                    score = self._score_position(crate.weight_kg, x, crate.length_cm)
                    if best is None or score > best[0]:
                        best = (score, crate, x, y)
        if best is None:
            return None
        _, crate, x, y = best
        return crate, x, y

    def _placement_options(self, crate: Crate, remaining: list[Crate]) -> int:
        if crate.height_cm > self.trailer.height_cm or not self._weight_ok(crate.weight_kg):
            return 0
        for x in range(self.grid_l - crate.length_cm + 1):
            for y in range(0, self.grid_w - crate.width_cm + 1):
                if self._single_fits(crate, x, y):
                    return 1
        for other in remaining:
            if other is crate or crate.width_cm + other.width_cm > self.grid_w:
                continue
            if not self._weight_ok(crate.weight_kg + other.weight_kg):
                continue
            row_length = max(crate.length_cm, other.length_cm)
            for x in range(self.grid_l - row_length + 1):
                if self._pair_fits(crate, other, x) or self._pair_fits(other, crate, x):
                    return 1
        return 0

    def plan(self, crates: Iterable[Crate], sort_key) -> LoadResult:
        remaining = sorted(list(crates), key=sort_key)
        overflow: list[str] = []

        while remaining:
            pair = self._find_best_pair(remaining)
            if pair is not None:
                c1, c2, x = pair
                y_left, y_right = 0, self.grid_w - c2.width_cm
                self._mark(x, y_left, c1.length_cm, c1.width_cm, c1)
                self._mark(x, y_right, c2.length_cm, c2.width_cm, c2)
                remaining.remove(c1)
                remaining.remove(c2)
                continue

            single = self._find_best_single(remaining)
            if single is not None:
                crate, x, y = single
                self._mark(x, y, crate.length_cm, crate.width_cm, crate)
                remaining.remove(crate)
                continue

            options = [(self._placement_options(c, remaining), c) for c in remaining]
            options.sort(key=lambda t: t[0])
            if options[0][0] == 0:
                overflow.append(options[0][1].asset_tag)
                remaining.remove(options[0][1])
                continue
            break

        for crate in remaining:
            overflow.append(crate.asset_tag)

        return LoadResult(
            trailer=self.trailer,
            placements=list(self.placements),
            overflow=overflow,
            left_weight_kg=self.left_weight,
            right_weight_kg=self.right_weight,
            cab_weight_kg=self.cab_weight,
            door_weight_kg=self.door_weight,
        )


def _filter_by_height(crates: list[Crate], max_height: float) -> tuple[list[Crate], list[str]]:
    ok: list[Crate] = []
    skipped: list[str] = []
    for crate in crates:
        if crate.height_cm > max_height:
            skipped.append(crate.asset_tag)
        else:
            ok.append(crate)
    return ok, skipped


def optimize_load(trailer: TrailerSpec, crates: list[Crate]) -> LoadResult:
    eligible, skipped = _filter_by_height(crates, trailer.height_cm)

    planner = TrailerLoadPlanner(trailer)
    result = planner.plan(eligible, sort_key=lambda c: (-c.weight_kg, -c.length_cm * c.width_cm))
    result.skipped_too_tall = skipped
    return result


def print_report(result: LoadResult, total_crates: int) -> None:
    t = result.trailer
    print(f"\n--- Load plan: {t.name} ---")
    print(f"Trailer: {t.length_cm:.0f} x {t.width_cm:.0f} x {t.height_cm:.0f} cm")
    print(f"Weight limit: {t.max_weight_kg:.0f} kg\n")

    if result.skipped_too_tall:
        print("Skipped (exceed trailer height):")
        for tag in result.skipped_too_tall:
            print(f"  - {tag}")
        print()

    print(f"Crates loaded: {result.loaded_count} / {total_crates}")
    print("Loaded asset tags:")
    for p in result.placements:
        print(f"  {p.asset_tag}")

    print(f"\nTotal weight loaded: {result.total_weight_kg:.2f} kg")
    print(f"Left: {result.left_weight_kg:.2f} kg | Right: {result.right_weight_kg:.2f} kg")
    balance = _balance_ratio(result.left_weight_kg, result.right_weight_kg) * 100
    print(f"Left/right imbalance: {balance:.1f}% (limit {BALANCE_TOLERANCE * 100:.0f}%)")
    print(f"Cab end (toward driver): {result.cab_weight_kg:.2f} kg")
    print(f"Door end (rear): {result.door_weight_kg:.2f} kg")

    if result.overflow:
        print(f"\n*** SECOND TRAILER REQUIRED ***")
        print(
            f"{len(result.overflow)} crate(s) could not fit on this trailer "
            f"({t.name}). Load these on a follow-up trailer:"
        )
        for tag in result.overflow:
            print(f"  {tag}")


def save_loading_plot(result: LoadResult, output_dir: Path) -> Path:
    t = result.trailer
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in t.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"load_plan_{safe_name}_{timestamp}.png"

    fig, ax = plt.subplots(figsize=(16, 5))
    ax.add_patch(
        plt.Rectangle( # type: ignore
            (0, 0),
            t.length_cm,
            t.width_cm,
            edgecolor="black",
            facecolor="#f5f5f5",
            linewidth=2,
        )
    )

    for p in result.placements:
        ax.add_patch(
            plt.Rectangle( # type: ignore
                (p.x, p.y),
                p.length_cm,
                p.width_cm,
                edgecolor="navy",
                facecolor="cyan",
                alpha=0.55,
                linewidth=1,
            )
        )
        ax.text(
            p.x + p.length_cm / 2,
            p.y + p.width_cm / 2,
            p.asset_tag[:10],
            ha="center",
            va="center",
            fontsize=6,
        )

    ax.annotate("", xy=(t.length_cm, t.width_cm / 2), xytext=(t.length_cm - 40, t.width_cm / 2),
                arrowprops=dict(arrowstyle="->", color="red", lw=2))
    ax.text(t.length_cm - 5, t.width_cm + 8, "Cab / driver", color="red", ha="right", fontsize=9)
    ax.text(5, t.width_cm + 8, "Doors (rear)", color="gray", ha="left", fontsize=9)

    summary = (
        f"Loaded: {result.loaded_count} crates | {result.total_weight_kg:.0f} kg\n"
        f"Left {result.left_weight_kg:.0f} kg | Right {result.right_weight_kg:.0f} kg | "
        f"Cab {result.cab_weight_kg:.0f} kg | Doors {result.door_weight_kg:.0f} kg"
    )
    ax.text(
        0.02,
        0.98,
        summary,
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
    )

    ax.set_xlim(-5, t.length_cm + 15)
    ax.set_ylim(-5, t.width_cm + 20)
    ax.set_xlabel("Length toward cab (cm)")
    ax.set_ylabel("Width (cm)")
    ax.set_title(
        f"Trailer load plan — {t.name}\n"
        f"{t.length_cm:.0f} x {t.width_cm:.0f} x {t.height_cm:.0f} cm | "
        f"max {t.max_weight_kg:.0f} kg",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_aspect("equal")
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def uk_trailer_spec(name: str = "UK") -> TrailerSpec:
    return TrailerSpec(
        name=name,
        length_cm=UK_TRAILER_LENGTH_CM,
        width_cm=UK_TRAILER_WIDTH_CM,
        height_cm=UK_TRAILER_HEIGHT_CM,
        max_weight_kg=UK_TRAILER_MAX_WEIGHT_KG,
    )


def _prompt_float(label: str, default: float) -> float:
    raw = input(f"{label} [{default}]: ").strip()
    return float(raw) if raw else default


def prompt_trailer() -> TrailerSpec:
    name = input("Trailer / load name (e.g. INT, UK, DUB): ").strip() or "UK"
    use_uk = input(
        f"Use standard UK trailer "
        f"({UK_TRAILER_LENGTH_CM} x {UK_TRAILER_WIDTH_CM} x {UK_TRAILER_HEIGHT_CM} cm, "
        f"{UK_TRAILER_MAX_WEIGHT_KG} kg)? [Y/n]: "
    ).strip().lower()
    if use_uk in ("", "y", "yes"):
        return uk_trailer_spec(name)

    length = _prompt_float("Length (cm), door to cab", UK_TRAILER_LENGTH_CM)
    width = _prompt_float("Width (cm)", UK_TRAILER_WIDTH_CM)
    height = _prompt_float("Height (cm)", UK_TRAILER_HEIGHT_CM)
    max_weight = _prompt_float("Maximum weight (kg)", UK_TRAILER_MAX_WEIGHT_KG)
    return TrailerSpec(name, length, width, height, max_weight)


def run_load_plan(
    trailer: TrailerSpec,
    data_path: Path | None = None,
    plots_dir: Path | None = None,
) -> LoadResult:
    data_path = data_path or Path(__file__).resolve().parent / "crate_data.xlsx"
    plots_dir = plots_dir or Path(__file__).resolve().parent / "load_plans"
    crates = load_crates_from_excel(data_path)
    result = optimize_load(trailer, crates)
    print_report(result, total_crates=len(crates))
    plot_path = save_loading_plot(result, plots_dir)
    print(f"\nPlot saved: {plot_path}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan crate loading for a trailer.")
    parser.add_argument(
        "--uk",
        action="store_true",
        help="Use standard UK trailer (1360x240x270 cm, 26000 kg) without prompts.",
    )
    parser.add_argument("--name", default="UK", help="Trailer / load name (with --uk).")
    args = parser.parse_args()

    trailer = uk_trailer_spec(args.name) if args.uk else prompt_trailer()
    run_load_plan(trailer)


if __name__ == "__main__":
    main()
