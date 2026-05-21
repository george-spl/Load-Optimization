"""
Desktop window for the load planner (no console required).
Double-click via Run Load Planner.bat or a packaged .exe.
"""

from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from Load_Optimization import (  # noqa: E402
    UK_TRAILER_HEIGHT_CM,
    UK_TRAILER_LENGTH_CM,
    UK_TRAILER_MAX_WEIGHT_KG,
    UK_TRAILER_WIDTH_CM,
    TrailerSpec,
    load_crates_from_excel,
    run_load_plan,
    uk_trailer_spec,
)


class LoadPlannerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Trailer Load Planner")
        self.minsize(640, 520)
        self._last_plot: Path | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}
        root = ttk.Frame(self, padding=10)
        root.pack(fill=tk.BOTH, expand=True)

        ttk.Label(root, text="Trailer / load name", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", **pad
        )
        self.name_var = tk.StringVar(value="UK-01")
        ttk.Entry(root, textvariable=self.name_var, width=40).grid(row=0, column=1, columnspan=2, sticky="ew", **pad)

        self.uk_var = tk.BooleanVar(value=True)
        uk = ttk.Checkbutton(
            root,
            text=f"Standard UK trailer ({UK_TRAILER_LENGTH_CM:.0f} x {UK_TRAILER_WIDTH_CM:.0f} x "
            f"{UK_TRAILER_HEIGHT_CM:.0f} cm, {UK_TRAILER_MAX_WEIGHT_KG:.0f} kg)",
            variable=self.uk_var,
            command=self._toggle_dims,
        )
        uk.grid(row=1, column=0, columnspan=3, sticky="w", **pad)

        dims = ttk.LabelFrame(root, text="Custom trailer dimensions", padding=8)
        dims.grid(row=2, column=0, columnspan=3, sticky="ew", **pad)
        self.dim_vars = {
            "length": tk.StringVar(value=str(int(UK_TRAILER_LENGTH_CM))),
            "width": tk.StringVar(value=str(int(UK_TRAILER_WIDTH_CM))),
            "height": tk.StringVar(value=str(int(UK_TRAILER_HEIGHT_CM))),
            "weight": tk.StringVar(value=str(int(UK_TRAILER_MAX_WEIGHT_KG))),
        }
        labels = [
            ("Length (cm), door to cab", "length"),
            ("Width (cm)", "width"),
            ("Height (cm)", "height"),
            ("Max weight (kg)", "weight"),
        ]
        self._dim_entries: list[ttk.Entry] = []
        for i, (label, key) in enumerate(labels):
            ttk.Label(dims, text=label).grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(dims, textvariable=self.dim_vars[key], width=14)
            entry.grid(row=i, column=1, sticky="w", pady=2)
            self._dim_entries.append(entry)
        self._toggle_dims()

        file_row = ttk.Frame(root)
        file_row.grid(row=3, column=0, columnspan=3, sticky="ew", **pad)
        ttk.Label(file_row, text="Crate data (.xlsx)").pack(side=tk.LEFT)
        self.file_var = tk.StringVar(value=str(APP_DIR / "crate_data.xlsx"))
        ttk.Entry(file_row, textvariable=self.file_var, width=50).pack(side=tk.LEFT, padx=6, fill=tk.X, expand=True)
        ttk.Button(file_row, text="Browse…", command=self._browse_file).pack(side=tk.LEFT)

        btn_row = ttk.Frame(root)
        btn_row.grid(row=4, column=0, columnspan=3, sticky="ew", **pad)
        self.run_btn = ttk.Button(btn_row, text="Run load plan", command=self._run_async)
        self.run_btn.pack(side=tk.LEFT)
        ttk.Button(btn_row, text="Open load_plans folder", command=self._open_plots_folder).pack(side=tk.LEFT, padx=8)
        ttk.Button(btn_row, text="Open latest plot", command=self._open_latest_plot).pack(side=tk.LEFT)

        ttk.Label(root, text="Results").grid(row=5, column=0, sticky="nw", **pad)
        self.output = scrolledtext.ScrolledText(root, height=16, wrap=tk.WORD, font=("Consolas", 10))
        self.output.grid(row=5, column=1, columnspan=2, sticky="nsew", **pad)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(5, weight=1)

        self.status = tk.StringVar(value="Ready.")
        ttk.Label(root, textvariable=self.status).grid(row=6, column=0, columnspan=3, sticky="w", **pad)

    def _toggle_dims(self) -> None:
        state = "disabled" if self.uk_var.get() else "normal"
        for entry in self._dim_entries:
            entry.configure(state=state)

    def _browse_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select crate data",
            initialdir=APP_DIR,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if path:
            self.file_var.set(path)

    def _trailer_spec(self) -> TrailerSpec:
        name = self.name_var.get().strip() or "UK"
        if self.uk_var.get():
            return uk_trailer_spec(name)
        try:
            return TrailerSpec(
                name=name,
                length_cm=float(self.dim_vars["length"].get()),
                width_cm=float(self.dim_vars["width"].get()),
                height_cm=float(self.dim_vars["height"].get()),
                max_weight_kg=float(self.dim_vars["weight"].get()),
            )
        except ValueError as exc:
            raise ValueError("Trailer dimensions must be numbers.") from exc

    def _run_async(self) -> None:
        self.run_btn.configure(state="disabled")
        self.status.set("Running…")
        thread = threading.Thread(target=self._run_plan, daemon=True)
        thread.start()

    def _run_plan(self) -> None:
        try:
            data_path = Path(self.file_var.get().strip())
            if not data_path.is_file():
                raise FileNotFoundError(f"Crate data not found:\n{data_path}")

            trailer = self._trailer_spec()
            load_crates_from_excel(data_path)

            result, plot_path, report = run_load_plan(
                trailer,
                data_path=data_path,
                plots_dir=APP_DIR / "load_plans",
                quiet=True,
            )
            self._last_plot = plot_path
            text = report + f"\n\nPlot saved:\n{plot_path}"
            self.after(0, lambda: self._show_success(text, bool(result.overflow)))
        except Exception as exc:
            self.after(0, lambda: self._show_error(str(exc)))
        finally:
            self.after(0, lambda: self.run_btn.configure(state="normal"))

    def _show_success(self, text: str, has_overflow: bool) -> None:
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.status.set("Done.")
        if has_overflow:
            messagebox.showwarning(
                "Second trailer required",
                "Some crates could not fit. See the results list for asset tags to load on a follow-up trailer.",
            )

    def _show_error(self, message: str) -> None:
        self.status.set("Error.")
        messagebox.showerror("Load plan failed", message)

    def _open_plots_folder(self) -> None:
        folder = APP_DIR / "load_plans"
        folder.mkdir(exist_ok=True)
        os.startfile(folder)

    def _open_latest_plot(self) -> None:
        if self._last_plot and self._last_plot.is_file():
            os.startfile(self._last_plot)
            return
        folder = APP_DIR / "load_plans"
        if not folder.is_dir():
            messagebox.showinfo("No plots yet", "Run a load plan first.")
            return
        plots = sorted(folder.glob("load_plan_*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        if plots:
            os.startfile(plots[0])
        else:
            messagebox.showinfo("No plots yet", "Run a load plan first.")


def main() -> None:
    app = LoadPlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
