> **Development status:** under active development — verify load plans before use in production.

# Load Optimization

A Python tool for planning how heavy crates are loaded onto truck trailers. It produces a console report and a labelled floor-plan image so multiple people can see **which trailer** a layout belongs to and **what still needs a second trailer**.

Crates are **never rotated**. The planner enforces **left/right weight balance**, prefers **heavier weight toward the cab** (driver end), and respects **trailer dimensions and maximum weight**.

---

## What it does

1. Reads crate dimensions and weights from an Excel file (`crate_data.xlsx`).
2. Asks for trailer size (or uses the standard UK preset).
3. Places crates in two phases, loading **from the cab end toward the doors** (heavy items first at the cab):
   - **Pairing** — two crates side-by-side when their combined width fits the trailer (left crate on the left wall, right crate on the right wall, same row).
   - **Chessboard** — remaining crates that cannot be paired go on the **left or right wall only**, one per row, alternating sides as rows step toward the doors.
4. Prints a load report and saves a PNG floor plan under `load_plans/`.
5. Lists any crates that do not fit with **`SECOND TRAILER REQUIRED`**.

Only crates that physically fit (space, height, weight limit, and balance rules) are loaded. Nothing is silently skipped.

---

## Quick start

### Work PC (no Python, no console)

Copy the **`Load Planner Package/`** folder to the target PC and double-click **`Load Planner.exe`**.

See **[DEPLOY_WORK_PC.md](DEPLOY_WORK_PC.md)** for IT setup, shortcuts, and troubleshooting.

### Developer machine

```powershell
cd "d:\github\Load Optimization"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Then either:

| Method | Command / action |
|--------|------------------|
| **Desktop app** | Double-click `Run Load Planner.bat` |
| **Console** | `python Load_Optimization.py` |
| **UK quick test** | `python Load_Optimization.py --uk --name UK-01` |
| **Build exe** | Double-click `build_exe.bat` |

---

## Loading rules (summary)

| Rule | Behaviour |
|------|-----------|
| Orientation | Fixed — length × width as stored; no turning crates |
| Pairing | If `width₁ + width₂ ≤ trailer width`, pair on left + right walls in the same row |
| Unpaired / wide crates | No partner with combined width ≤ trailer width → chessboard (one crate per row on a wall) |
| Chessboard | Left wall (`y = 0`) or right wall (`y = trailer width − crate width`); rows alternate L/R; each row steps **toward the doors** from the cab |
| Left/right balance | Final loaded weight imbalance must stay within **10%** (`BALANCE_TOLERANCE` in code) |
| Cab weight | Heavier crates are preferentially placed toward the **cab end** when scoring positions |
| Mixed loads | Narrow crates pair first; remaining wide crates continue in chessboard on the same trailer |
| Height | Crates taller than the trailer are excluded and listed as skipped |
| Weight | Total loaded weight must not exceed the trailer maximum |

---

## Floor plan coordinates

Viewed from the **rear doors**, facing the **cab**:

```
  Doors (rear)                              Cab / driver
       x = 0  ──────────────────────────────────────►  x = length

       y = 0 (left wall)  ·····················  y = width (right wall)
```

Chessboard rows use **staggered x positions** (cab row first at `x = length − crate length`, then each next row at `min(x) − crate length`) so wide crates on opposite walls do not overlap in the centre aisle.

---

## Crate data (Excel)

Default file: **`crate_data.xlsx`** in the project folder (same folder as the exe or scripts).

### Required columns

| Column | Description |
|--------|-------------|
| `Asset Tag` | Unique crate identifier (string) |
| `Gross Weight (kg)` | Weight in kilograms |

### Dimensions (one of the following)

**Option A — separate columns (recommended for production)**

- `Length (cm)`, `Width (cm)`, `Height (cm)`

**Option B — single size string**

- `Size (cm)` as **`length x width x height`** (e.g. `147x131x257`)

Length runs along the trailer (door to cab). Width runs across the trailer. Height is vertical clearance.

Other columns (`Crate ID`, `Crate Type`, `Location`, etc.) are ignored by the planner.

---

## Running the planner

### Desktop app (recommended for users)

Double-click **`Run Load Planner.bat`** (requires `.venv` on the machine) or **`Load Planner.exe`** from the deploy package.

The window lets you set trailer name, UK standard or custom dimensions, browse for Excel, run the plan, and open the latest plot.

### Console (developers / testing)

```powershell
python Load_Optimization.py
```

Prompts:

1. **Trailer / load name** — e.g. `UK-01`, `UK-WIDE` (used on plots and in filenames).
2. **Use standard UK trailer? [Y/n]** — **Y** or Enter for the preset; **n** for custom sizes (UK values shown as defaults).

Quick UK run without prompts:

```powershell
python Load_Optimization.py --uk --name UK-01
```

### Standard UK trailer

| Dimension | Value |
|-----------|--------|
| Length | 1360 cm (door to cab) |
| Width | 240 cm |
| Height | 270 cm |
| Max weight | 26,000 kg |

---

## Output

### Console / app report

- Trailer name and dimensions
- Crates skipped (too tall)
- Count loaded vs total and asset tags
- Total weight, left/right split, imbalance % (with 10% limit shown)
- Weight toward cab vs doors
- **`SECOND TRAILER REQUIRED`** — asset tags for a follow-up load

### Floor plan PNG

```
load_plans/load_plan_<trailer-name>_<timestamp>.png
```

Includes trailer outline, crate positions, cab/door labels, and a summary box.

---

## Building the standalone app

From the project folder (path must not break — the batch file handles spaces in `Load Optimization`):

```cmd
build_exe.bat
```

This will:

1. Install dependencies and PyInstaller (if needed)
2. Build **`dist\Load Planner.exe`**
3. Copy the exe (and `crate_data.xlsx`) into **`Load Planner Package/`** — the folder to distribute

If the build fails, the script stops and does **not** copy an old exe.

**Deploy to work PCs:** copy the entire **`Load Planner Package/`** folder.

---

## Generating test data

```powershell
python dummy_generator.py
```

Creates or overwrites `crate_data.xlsx` with 25 random crates (~800–900 kg). Default sizes mix **narrow** crates (e.g. 161×111 cm — can pair two across) and **wide** crates (~131 cm width — chessboard only). Edit `crate_sizes` in the script to test all-wide or all-narrow scenarios.

---

## Project structure

```
Load Optimization/
├── Load_Optimization.py      # Core planner
├── load_planner_gui.py       # Desktop UI
├── dummy_generator.py        # Test Excel generator
├── Run Load Planner.bat      # Launch GUI (dev, uses .venv)
├── build_exe.bat             # Build exe + refresh deploy package
├── crate_data.xlsx           # Input data
├── requirements.txt
├── load_plans/               # Generated PNG floor plans
├── Load Planner Package/     # Ready-to-copy deploy folder (exe + data)
├── README.md
├── DEPLOY_WORK_PC.md         # IT / work PC guide
└── LICENSE
```

Generated by builds (gitignored): `build/`, `dist/`, `Load Planner.spec`.

---

## How the algorithm works

**Phase 1 — Pairing**  
Find the best pair that fits side-by-side on the walls (space, height, weight limit, and left/right balance). Heavier pairs are preferentially placed toward the cab. Repeat until no pair fits.

**Phase 2 — Chessboard**  
Each remaining crate goes on the **left or right wall only**, one per row. Rows fill **cab → doors**. Sides alternate row-by-row (strict L/R/L/R… or R/L/R/L… — the planner picks whichever start side gives better balance).

When choosing a crate for each row, the planner **forecasts final left/right balance** (assigning heavier remaining crates to the side with fewer rows in the pattern) and picks the option with the lowest projected imbalance, then cab-weight bias as tie-breaker.

Brief imbalance mid-load is allowed when the next row is on the opposite wall. The first chessboard row after pairing is always permitted so alternation can begin even when pairs already loaded both sides.

**Typical outcomes**

| Crate mix | Behaviour |
|-----------|-----------|
| Mostly narrow (pairs fit) | Several pair rows at the cab, then chessboard for leftovers |
| All wide (no pairs) | Chessboard only — often 8–9 rows on a 1360 cm UK trailer |
| Overflow | Length, height, weight, or balance rules block further crates → **SECOND TRAILER REQUIRED** |

---

## Limitations

- Greedy planner — good operational layouts, not guaranteed optimal packing or minimum trailer count.
- Odd chessboard row counts (e.g. 9 rows) need uneven left/right weight to stay within 10%; the planner optimises for this but cannot always load every crate.
- 1 cm grid — dimensions rounded up to whole centimetres.
- One trailer per run — overflow crates need a second run or trailer.
- Balance tolerance default 10% — change `BALANCE_TOLERANCE` in `Load_Optimization.py` if needed.

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| `ModuleNotFoundError: openpyxl` | `pip install -r requirements.txt` |
| `build_exe.bat` path error | Use the updated script (`%CD%` paths); folder name can contain spaces |
| Build succeeded but old exe | Script now fails loudly if PyInstaller errors |
| Only pairs loaded, door end empty | Rebuild from current code — chessboard must run after pairing |
| High left/right imbalance | Odd row count (e.g. 9 chessboard rows) needs heavier crates on the side with **fewer** rows; re-run with latest planner |
| Many crates in overflow | Trailer may be full — expected; use second trailer list |
| Wrong layout shape | Confirm `Size (cm)` is **length x width x height** |
| Plot not found | Check `load_plans/` next to the exe or script |

---

## Example commands

```powershell
# Desktop app (dev)
Run Load Planner.bat

# Console — custom trailer
python Load_Optimization.py

# Console — UK preset
python Load_Optimization.py --uk --name UK-WIDE

# Regenerate test data, then plan
python dummy_generator.py
python Load_Optimization.py --uk --name UK-WIDE

# Rebuild deploy package
build_exe.bat
```

---

## License

See **`LICENSE`**.
