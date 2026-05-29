Load Planner — work PC package
================================

Double-click Load Planner.exe to open the app.
No Python, VS Code, or command window needed.


CONTENTS
--------

  Load Planner.exe   The application
  crate_data.xlsx    Crate list (replace with your export)
  load_plans/        Floor-plan PNGs are saved here
  README.txt         This file


QUICK START
-----------

1. Put your crate Excel file here as crate_data.xlsx,
   or click Browse in the app to pick another file.

2. Enter a trailer / load name (e.g. UK-01, UK-WIDE).
   This name appears on the plot and in the filename.

3. Tick "Standard UK trailer" or enter custom dimensions.

4. Click Run load plan.

5. Click Open latest plot to view the layout,
   or Open load_plans folder to see all saved PNGs.


STANDARD UK TRAILER
-------------------

  Length:     1360 cm  (door to cab)
  Width:      240 cm
  Height:     270 cm
  Max weight: 26,000 kg


EXCEL FILE FORMAT
-----------------

Required columns:
  Asset Tag
  Gross Weight (kg)

Dimensions — either:
  Length (cm), Width (cm), Height (cm)
  — or —
  Size (cm)  as  length x width x height  (e.g. 147x131x257)


WHAT TO EXPECT
--------------

  - Crates are never rotated.
  - Loading runs cab end first, then toward the doors.
  - Pairs load side-by-side when combined width fits the trailer.
  - Remaining unpaired crates alternate left/right on the walls (chessboard).
  - Left/right weight balance is kept within 10%.
  - Crates that do not fit are listed as SECOND TRAILER REQUIRED.
  - Plots save to load_plans/ as load_plan_<name>_<date>.png


UPDATING DATA
-------------

Replace crate_data.xlsx with a new export (same column names).
No reinstall needed — open the app and run again.


TROUBLESHOOTING
---------------

  Python was not found     You do not need Python — use Load Planner.exe only.
  Excel not found          Put crate_data.xlsx in this folder or use Browse.
  Plot did not open        Check the load_plans folder — the PNG is saved there.
  SmartScreen warning      Ask IT to allowlist Load Planner.exe (unsigned app).
  Only pairs, no door rows Re-download Load Planner Package (rebuilt with build_exe.bat).


FOR DEVELOPERS — REBUILD THIS PACKAGE
--------------------------------------

From the main project folder (Load Optimization), run:

  build_exe.bat

That rebuilds Load Planner.exe and refreshes this folder automatically.
