# Running on a work PC (no VS Code, no console)

Three ways to run the tool. For most staff, use **Option 1** or **Option 2**.

---

## Option 1 — Deploy package (recommended)

Copy this folder to a network drive or each PC:

```
Load Planner Package/
├── Load Planner.exe      ← double-click this
├── crate_data.xlsx       ← replace with your export
├── load_plans/           ← plots save here
└── README.txt
```

### What users do

1. Double-click **`Load Planner.exe`**.
2. Enter a trailer name (e.g. `UK-01`, `UK-WIDE`).
3. Tick **Standard UK trailer** or enter custom dimensions.
4. Select the Excel file (**Browse** if not using `crate_data.xlsx` in this folder).
5. Click **Run load plan**.
6. Click **Open latest plot** or **Open load_plans folder**.

No Python, VS Code, or command window required.

### Updating crate data

Replace **`crate_data.xlsx`** with a new export (same column names). No reinstall needed.

---

## Option 2 — Full project folder (Python on PC)

Use when IT allows Python but users should not use a console.

```
Load Optimization/
├── Run Load Planner.bat      ← users double-click this
├── load_planner_gui.py
├── Load_Optimization.py
├── crate_data.xlsx
├── requirements.txt
├── load_plans/
└── .venv/                    ← required (see setup below)
```

`Run Load Planner.bat` starts the GUI with `pythonw` (no black console window).

### One-time IT setup

**A) Copy the project including `.venv`** from a machine where `pip install -r requirements.txt` was already run.

**B) Install Python on the work PC**

1. Install [Python 3.10+](https://www.python.org/downloads/) — tick **Add python.exe to PATH**.
2. In Command Prompt, from the project folder:

   ```cmd
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

3. Users double-click **`Run Load Planner.bat`**.

---

## Option 3 — Console (developers / testing only)

```cmd
python Load_Optimization.py
```

Or:

```cmd
python Load_Optimization.py --uk --name UK-01
```

Not recommended for warehouse or office staff.

---

## Building the deploy package (developers)

On a dev machine, from the **`Load Optimization`** project folder:

```cmd
build_exe.bat
```

Requirements:

- `.venv` exists with dependencies installed
- Project path may contain spaces (e.g. `Load Optimization`) — the batch file handles this

On success:

- **`dist\Load Planner.exe`** — intermediate build output
- **`Load Planner Package\`** — refreshed deploy folder to copy to work PCs

If PyInstaller fails, the script reports **Build FAILED** and does not copy an outdated exe.

To rebuild after code changes, run `build_exe.bat` again and redistribute **`Load Planner Package/`**.

---

## Comparison

| Method | Python on PC? | Console? | Best for |
|--------|---------------|----------|----------|
| `Load Planner Package/` exe | No | No | Locked-down work PCs |
| `Run Load Planner.bat` + venv | Yes | No | Shared dev/network folder |
| `Load_Optimization.py` | Yes | Yes | Testing / scripts |

---

## Standard UK trailer

| Dimension | Value |
|-----------|--------|
| Length | 1360 cm (door to cab) |
| Width | 240 cm |
| Height | 270 cm |
| Max weight | 26,000 kg |

---

## Desktop shortcut (optional)

1. Right-click **`Load Planner.exe`** or **`Run Load Planner.bat`** → **Send to** → **Desktop (create shortcut)**.
2. Rename to **Trailer Load Planner**.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| “Python was not found” | Use **`Load Planner.exe`** from the deploy package, or install Python + `.venv` |
| `build_exe.bat`: script file does not exist | Re-download `build_exe.bat` (fixed for paths with spaces); run from project folder |
| Build says succeeded but app is old | Check for **Build FAILED** message; delete old exe and rebuild |
| Window flashes and closes | Use **`Run Load Planner.bat`** or **`Load Planner.exe`**, not raw `python load_planner_gui.py` |
| Excel file not found | Put `crate_data.xlsx` next to the exe, or use **Browse** in the app |
| Plot does not open | Click **Open load_plans folder** — the PNG is saved even if the viewer fails |
| Windows SmartScreen warning | Unsigned exe — IT may need to allowlist **`Load Planner.exe`** |
| All crates in overflow | Trailer may be full; check report for **SECOND TRAILER REQUIRED** list |
| Only pairs on plot, nothing toward doors | Rebuild with latest `build_exe.bat` — chessboard phase should follow pairing |
| Left/right imbalance over 10% in report | Rebuild with latest exe; planner forecasts balance when picking chessboard rows |

---

## What the app does (brief)

- Loads crates from Excel (fixed orientation — no rotation).
- Fills the trailer **from the cab end toward the doors** (heavy items first at the cab).
- **Pairs** crates that fit side-by-side on the left and right walls.
- Places remaining **unpaired / wide** crates in a **chessboard** pattern (one per row, alternating left/right walls toward the doors).
- Enforces left/right weight balance (10% tolerance) and trailer weight limit.
- Saves a labelled floor-plan PNG and lists crates that need a **second trailer**.

Full details: **[README.md](README.md)**
