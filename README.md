# Load Optimization — Trailer Load Planner

A **proof-of-concept** Python application that demonstrates how a recurring logistics problem can be identified, broken down into rules, and turned into a **working prototype** with a visual output.

It reads crate data from Excel, applies loading rules inspired by real warehouse transport practice, and produces a text report plus a labelled floor-plan image — enough to **show the idea works**, not to replace established load-planning processes without further validation.

> **Project intent:** This is a **demonstration project**, not production software. It was built to show problem-spotting, solution design, and hands-on prototyping skills. It has **not** been validated against live operational data and is **not** intended for immediate rollout.

---

## Overview

In warehouse and transport operations, loading a trailer is not only about fitting crates inside the box. Loaders must respect **weight limits**, keep the trailer **balanced left and right**, and place **heavier items toward the cab** for safe handling. Doing this manually for dozens of crates is slow and error-prone.

**The problem I identified:** teams need a repeatable way to draft a load layout and see what will not fit — before committing time on the bay.

**What this project demonstrates:** that a rule-based planner can encode those constraints, run against an Excel export, and produce something a supervisor could review — as a **starting point for discussion**, not a final load instruction.

---

## Project intent — proof of concept

| | |
|---|---|
| **What this is** | A working prototype that proves the approach is feasible |
| **What this is not** | A finished product ready for immediate use on the warehouse floor |
| **Data used** | Dummy / test data during development — not validated against live company exports |
| **Before any real use** | Comprehensive testing with real crate data, loader/supervisor review, process sign-off, and likely significant adjustments |
| **Why it exists** | To show I can **spot a practical problem**, **propose a structured solution**, and **build something that runs** |

### What I want a reviewer to take away

1. **Problem-solving** — I noticed a gap in how load planning is done and defined concrete rules to address it.
2. **Building** — I turned that into functioning Python software with input, logic, output, and a simple UI.
3. **Pragmatism** — I used modern tools (including a Cursor AI agent) to package and refine the prototype responsibly, while owning the problem definition and validation of behaviour.

If asked *“Would you deploy this tomorrow?”* — the honest answer is **no**. This would need exhaustive testing with real data, stakeholder input, and engineering hardening before it could be considered for a pilot at my company.

---

## About this project

This tool addresses a **workplace-inspired problem** — planning trailer loads for heavy crates — simplified into a demonstrable prototype.

### How it was built

| Aspect | Detail |
|--------|--------|
| **Core development** | Written in **Python**, using **foundational programming concepts** — variables, functions, loops, conditionals, file I/O, and basic object-oriented structure (`dataclass`, simple classes). |
| **Learning approach** | Built while following **Python tutorials and documentation** (pandas for Excel, matplotlib for plotting, standard library modules such as `pathlib` and `argparse`). |
| **Libraries used** | `pandas`, `openpyxl`, `numpy`, `matplotlib`, `tkinter` (GUI), and `faker` (test data only). |
| **Packaging & refinement** | A **Cursor AI agent** was used to help package the application for demonstration — building the standalone `.exe` with PyInstaller, fixing deployment issues, refining the loading algorithm, and improving documentation. |
| **What I own** | Identifying the problem, defining the loading rules, testing behaviour against scenarios, and judging whether outputs are sensible. |
| **What the AI assisted with** | Implementation details, debugging edge cases, PyInstaller configuration, and documentation structure. |

This is intentionally **not** an enterprise optimisation engine. It is a **focused proof of concept** — rule-based, understandable, and built with accessible Python skills plus AI-assisted polish so it can be **shown and discussed**, not silently dropped into a live process.

## What this tool is

- A **proof-of-concept load planner** for fixed-orientation crates on a rectangular trailer.
- A **demonstration** that a workplace problem can be decomposed into rules and implemented in code.
- A **decision-support sketch** — suggests placements and highlights overflow for human review.
- A **report generator** — console text, GUI output, and PNG floor plan.
- A **runnable prototype** (`Load Planner.exe`) so the idea can be shown without a Python install.

## What this tool is not

- **Not** ready for immediate operational deployment — developed with dummy data; real use would require full validation.
- **Not** a certified load-securing or road-legal compliance system.
- **Not** a global optimiser — it uses a **greedy, two-phase heuristic**, not exhaustive optimisation.
- **Not** a warehouse management system (WMS), route planner, or inventory tool.
- **Not** a 3D stacking solver — crates are treated as a **2D floor plan**; height is only checked against a maximum.
- **Not** production-hardened software — no automated test suite, audit trail, or formal sign-off process.

## What it does

| Capability | Description |
|------------|-------------|
| **Read Excel input** | Loads crate asset tags, weights, and dimensions from `crate_data.xlsx`. |
| **Trailer configuration** | Default preset or custom length, width, height, and max weight via GUI/console. |
| **Two-phase loading** | **Phase 1 — Pairing:** places two crates side-by-side when combined width fits. **Phase 2 — Chessboard:** places remaining crates one per row on alternating left/right walls. |
| **Cab-first loading** | Fills from the **cab end toward the doors**, preferring heavier weight at the cab. |
| **Balance enforcement** | Keeps left/right weight imbalance within **10%** (configurable in code). |
| **Constraint checks** | Respects trailer length, width, height, and maximum gross weight. |
| **Overflow reporting** | Lists crates that cannot fit under **`SECOND TRAILER REQUIRED`**. |
| **Visual output** | Saves a labelled PNG floor plan to `load_plans/`. |
| **Desktop GUI** | Simple tkinter window for non-developers (trailer name, Excel browse, run plan, open plot). |
| **Standalone executable** | PyInstaller-built `.exe` for work PCs without Python. |

## What it does not do

| Limitation | Detail |
|------------|--------|
| **Rotate crates** | Orientation is fixed as stored in Excel. |
| **Stack vertically** | No multi-layer 3D packing — one floor level only. |
| **Guarantee optimal fill** | May leave usable space unfilled; may not minimise trailer count. |
| **Load multiple trailers automatically** | One trailer per run; overflow must be planned separately. |
| **Integrate with live systems** | No API, ERP, or WMS connection — Excel in, report out. |
| **Handle lashing, strapping, or axle limits** | Weight is split left/right and cab/door only — not per-axle. |
| **Replace human judgement** | Output is a **proposal** for loaders and supervisors to review. |

---

## Loading rules (business logic)

Viewed from the **rear doors**, facing the **cab**:

```
  Doors (rear)                              Cab / driver
       x = 0  ──────────────────────────────────────►  x = length
       y = 0 (left wall)  ·················  y = width (right wall)
```

| Rule | Behaviour |
|------|-----------|
| Orientation | Fixed — length × width as stored; crates are never turned |
| Pairing | If `width₁ + width₂ ≤ trailer width`, pair on left + right walls in the same row |
| Chessboard | Unpaired crates go on one wall only; rows alternate L/R toward the doors |
| Balance | Left/right weight imbalance ≤ **10%** (`BALANCE_TOLERANCE` in `Load_Optimization.py`) |
| Cab bias | Heavier items scored toward the cab end |
| Height filter | Crates taller than the trailer are skipped and listed in the report |
| Weight limit | Total loaded weight must not exceed trailer maximum |

Chessboard rows use staggered **x** positions so wide crates on opposite walls do not overlap in the centre aisle.

---

## Technology stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Data input | pandas, openpyxl |
| Planning grid | numpy |
| Visualisation | matplotlib |
| Desktop UI | tkinter (standard library) |
| Packaging | PyInstaller |
| Test data | faker (`dummy_generator.py`) |

---

## Quick start

### End users (work PC — no Python)

1. Copy **`Load Planner Package/`** to the target PC.
2. Double-click **`Load Planner.exe`**.
3. See **[DEPLOY_WORK_PC.md](DEPLOY_WORK_PC.md)** for full instructions.

### Developers

```powershell
cd "D:\github\Load Optimization"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

| Action | Command |
|--------|---------|
| Desktop app | Double-click `Run Load Planner.bat` |
| Console | `python Load_Optimization.py` |
| Quick test | `python Load_Optimization.py` (accept the default trailer preset when prompted) |
| Build exe | Double-click `build_exe.bat` |
| Generate test data | `python dummy_generator.py` |

---

## Input — Excel format

Default file: **`crate_data.xlsx`** (same folder as the script or exe).

**Required columns**

| Column | Description |
|--------|-------------|
| `Asset Tag` | Unique crate identifier |
| `Gross Weight (kg)` | Weight in kilograms |

**Dimensions** — either separate columns (`Length (cm)`, `Width (cm)`, `Height (cm)`) or a single `Size (cm)` field as `length x width x height` (e.g. `147x131x257`).

Length runs door-to-cab; width runs across the trailer; height is vertical clearance. Other columns are ignored.

---

## Output

**Text report** — trailer details, loaded/skipped/overflow crates, total weight, left/right split, imbalance %, cab vs door weight.

**Floor plan PNG** — saved to:

```
load_plans/load_plan_<trailer-name>_<timestamp>.png
```

---

## Trailer configuration

Trailer **length**, **width**, **height**, and **maximum weight** are entered in the app or at the console prompt. A **default preset** is available for quick demos; custom dimensions can be used for any trailer type.

---

## How the algorithm works (summary)

**Phase 1 — Pairing**  
Repeatedly finds the best pair that fits side-by-side on the walls within space, height, weight, and balance limits. Heavier pairs are preferentially placed toward the cab.

**Phase 2 — Chessboard**  
Each remaining crate is placed on the left or right wall only, one per row, filling cab → doors with strict L/R alternation. The planner forecasts final left/right balance when choosing each crate and assigns heavier items toward the side with fewer rows when needed.

This is a **greedy heuristic** — fast and understandable, but not mathematically optimal.

---

## Project structure

```
Load Optimization/
├── Load_Optimization.py       # Core planner logic
├── load_planner_gui.py        # Desktop UI (tkinter)
├── dummy_generator.py         # Test Excel generator
├── Run Load Planner.bat       # Launch GUI (dev environment)
├── build_exe.bat              # Build exe and refresh deploy package
├── crate_data.xlsx            # Input data
├── requirements.txt
├── load_plans/                # Generated PNG floor plans
├── Load Planner Package/      # Deploy folder (exe + data)
├── README.md                  # This file
├── DEPLOY_WORK_PC.md          # Work PC deployment guide
└── LICENSE
```

Build artefacts (gitignored): `build/`, `dist/`, `Load Planner.spec`.

---

## Building the standalone app

From the project folder:

```cmd
build_exe.bat
```

This installs PyInstaller if needed, builds `dist\Load Planner.exe`, and copies it (with `crate_data.xlsx`) into **`Load Planner Package/`**. The script fails loudly if the build does not succeed — it will not copy an outdated exe.

---

## Possible next steps (if this were taken further)

These are **not part of the current PoC** — they illustrate how the idea could evolve after stakeholder buy-in:

- Validation with **real company Excel exports** and loader feedback
- Comprehensive **automated tests** for balance, pairing, and edge cases
- **Pilot** with one team, clear disclaimers, and a manual sign-off step
- Per-axle weight modelling, multi-trailer planning, or WMS integration

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| `ModuleNotFoundError: openpyxl` | Run `pip install -r requirements.txt` |
| Build fails on paths with spaces | Use the current `build_exe.bat` (uses `%CD%`) |
| Many crates in overflow | Trailer may be full — expected; use the second-trailer list |
| Wrong layout shape | Confirm `Size (cm)` is **length x width x height** |
| Plot not found | Check `load_plans/` next to the exe or script |
| Windows SmartScreen warning | Unsigned exe — IT may need to allowlist `Load Planner.exe` |

---

## License

See **`LICENSE`**.
