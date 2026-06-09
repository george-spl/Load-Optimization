# Deployment Guide — Work PCs

This guide explains how to **run and demonstrate** the Trailer Load Planner on a PC without Python installed.

> **Note:** The packaged `.exe` exists so the **proof of concept can be shown easily** (e.g. in an interview or demo). It is not an endorsement of immediate operational rollout. See **[README.md](README.md)** for project intent and limitations.

---

## Who this guide is for

- **Warehouse / logistics staff** — run load plans from Excel without using a command line.
- **IT support** — install or update the application on locked-down PCs.
- **Reviewers** — understand how the packaged app relates to the source project.

The packaged application (`Load Planner.exe`) is built from the Python source using **PyInstaller**, with packaging support from a **Cursor AI agent**. End users do not need Python installed.

---

## Option 1 — Deploy package (recommended)

Copy this folder to a network drive or each PC:

```
Load Planner Package/
├── Load Planner.exe      ← double-click to run
├── crate_data.xlsx       ← replace with your export
├── load_plans/           ← floor-plan PNGs save here
└── README.txt
```

### User steps

1. Double-click **`Load Planner.exe`**.
2. Enter a trailer / load name (e.g. `UK-01`) — this appears on the plot and in filenames.
3. Tick **Standard UK trailer** or enter custom dimensions.
4. Select the Excel file (**Browse** if not using `crate_data.xlsx` in this folder).
5. Click **Run load plan**.
6. Click **Open latest plot** or **Open load_plans folder**.

No Python, IDE, or command window is required.

### Updating crate data

Replace **`crate_data.xlsx`** with a new export using the same column names. No reinstall is needed — open the app and run again.

---

## Option 2 — Full project folder (Python available)

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

`Run Load Planner.bat` starts the GUI with `pythonw` (no console window).

### One-time IT setup

**A)** Copy the project including `.venv` from a machine where dependencies are already installed.

**B)** Install Python on the work PC:

1. Install [Python 3.10+](https://www.python.org/downloads/) — tick **Add python.exe to PATH**.
2. From the project folder in Command Prompt:

   ```cmd
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

3. Users double-click **`Run Load Planner.bat`**.

---

## Option 3 — Console (developers / testing)

```cmd
python Load_Optimization.py
python Load_Optimization.py --uk --name UK-01
```

Not intended for warehouse or office staff.

---

## Building the deploy package (developers)

From the **`Load Optimization`** project folder:

```cmd
build_exe.bat
```

**Requirements:** `.venv` exists with dependencies installed. The batch file handles project paths that contain spaces.

**On success:**

- `dist\Load Planner.exe` — intermediate build output
- `Load Planner Package\` — refreshed folder to copy to work PCs

If PyInstaller fails, the script reports **Build FAILED** and does not copy an outdated exe. After code changes, run `build_exe.bat` again and redistribute **`Load Planner Package/`**.

---

## Deployment comparison

| Method | Python required? | Console? | Best for |
|--------|------------------|----------|----------|
| `Load Planner Package/` exe | No | No | Locked-down work PCs |
| `Run Load Planner.bat` + venv | Yes | No | Shared network folder |
| `Load_Optimization.py` | Yes | Yes | Development and testing |

---

## Standard UK trailer preset

| Dimension | Value |
|-----------|--------|
| Length | 1360 cm (door to cab) |
| Width | 240 cm |
| Height | 270 cm |
| Max weight | 26,000 kg |

---

## What the application does (summary)

- Reads crate data from Excel (fixed orientation — no rotation).
- **Pairs** crates that fit side-by-side on the left and right walls.
- Places remaining crates in a **chessboard** pattern (one per row, alternating walls, cab → doors).
- Enforces left/right weight balance (10% tolerance) and trailer weight limit.
- Saves a labelled floor-plan PNG and lists crates needing a **second trailer**.

**What it does not do:** rotate crates, stack in 3D, guarantee minimum trailer count, or replace qualified human review. See **[README.md](README.md)** for full scope.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| “Python was not found” | Use **`Load Planner.exe`** from the deploy package |
| Excel file not found | Place `crate_data.xlsx` next to the exe, or use **Browse** |
| Plot does not open | Click **Open load_plans folder** — the PNG is saved even if the viewer fails |
| Windows SmartScreen warning | Unsigned exe — IT may need to allowlist **`Load Planner.exe`** |
| All crates in overflow | Trailer may be full — check **SECOND TRAILER REQUIRED** in the report |
| Outdated behaviour after update | Rebuild with `build_exe.bat` and redistribute **`Load Planner Package/`** |

---

## Optional — desktop shortcut

1. Right-click **`Load Planner.exe`** → **Send to** → **Desktop (create shortcut)**.
2. Rename to **Trailer Load Planner**.
