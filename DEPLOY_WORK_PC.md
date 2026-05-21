# Running on a work PC (no VS Code, no console)

Three ways to run the tool, from simplest for IT to best for end users.

---

## Option 1 — Double-click app (recommended)

### What users see

1. Double-click **`Run Load Planner.bat`** (or **`Load Planner.exe`** if IT built one).
2. A normal Windows window opens — no black console, no VS Code.
3. Enter trailer name, tick UK standard or enter custom sizes, pick the Excel file.
4. Click **Run load plan**.
5. Click **Open latest plot** to view the floor plan PNG.

### Folder to copy to the work PC

Copy the whole project folder, or at minimum:

```
Load Optimization/
├── Run Load Planner.bat      ← double-click this
├── load_planner_gui.py
├── Load_Optimization.py
├── crate_data.xlsx           ← your crate list
├── requirements.txt
├── load_plans/               ← empty folder (plots save here)
└── .venv/                    ← only if you copied the dev venv (see below)
```

### One-time setup (IT)

**A) Copy the project including `.venv` from a machine where you already ran `pip install -r requirements.txt`**

- Easiest if IT allows copying folders.
- `Run Load Planner.bat` uses `.venv\Scripts\pythonw.exe` (no console window).

**B) Install Python on the work PC**

1. Install [Python 3.10+](https://www.python.org/downloads/) — tick **“Add python.exe to PATH”**.
2. Open Command Prompt in the project folder:

   ```cmd
   python -m venv .venv
   .venv\Scripts\pip install -r requirements.txt
   ```

3. Users double-click **`Run Load Planner.bat`**.

---

## Option 2 — Standalone `.exe` (no Python on work PCs)

Build once on a developer machine, then distribute.

```cmd
build_exe.bat
```

Output: **`dist\Load Planner.exe`**

### Deploy package for users

```
Load Planner/
├── Load Planner.exe
├── crate_data.xlsx
└── load_plans/
```

Users double-click **`Load Planner.exe`**.  
Keep `crate_data.xlsx` in the **same folder** as the exe (or use **Browse** in the app to pick another file).

> Re-run `build_exe.bat` after code changes. Windows SmartScreen may warn on unsigned exes — IT may need to allowlist the file.

---

## Option 3 — Console version (IT / power users only)

```cmd
python Load_Optimization.py
```

Or UK quick run:

```cmd
python Load_Optimization.py --uk --name UK-01
```

This uses text prompts in a command window — not ideal for most warehouse/office staff.

---

## Comparison

| Method | Python needed on PC? | Console? | Best for |
|--------|----------------------|----------|----------|
| `Run Load Planner.bat` + venv | Yes (venv or install) | No | Shared network folder |
| `Load Planner.exe` | No | No | Locked-down PCs |
| `Load_Optimization.py` | Yes | Yes | Testing / scripts |

---

## Desktop shortcut (optional)

1. Right-click **`Run Load Planner.bat`** → **Send to** → **Desktop (create shortcut)**.
2. Rename to **Trailer Load Planner**.
3. Right-click shortcut → **Properties** → **Change icon** if desired.

---

## Troubleshooting on work PCs

| Problem | Fix |
|---------|-----|
| “Python was not found” | Install Python or use the `.exe` build |
| Window flashes and closes | Use `Run Load Planner.bat`, not `python load_planner_gui.py` from an unknown path |
| Excel file not found | Put `crate_data.xlsx` next to the bat/exe, or Browse to your file |
| Plot does not open | Click **Open load_plans folder** — PNG is there even if the viewer failed |
| Antivirus blocks `.exe` | Ask IT to allowlist `Load Planner.exe` |

---

## Updating crate data

Replace **`crate_data.xlsx`** with a new export from your system (same column names). No restart or reinstall needed — open the app and run again.
