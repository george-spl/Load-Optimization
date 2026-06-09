Trailer Load Planner — Demonstration Package
============================================

Proof-of-concept desktop tool: plans crate loading on truck trailers from Excel,
produces a report and floor-plan image.

Double-click Load Planner.exe to run a demo. No Python required.


ABOUT THIS SOFTWARE
-------------------

This is a PROOF OF CONCEPT, not production software.

It was built to demonstrate that a workplace loading problem can be identified,
broken into rules, and turned into a working prototype. Development used dummy
/test data — not validated for live operational use.

Built in Python (basic programming + tutorials). Packaged with PyInstaller;
Cursor AI agent assisted with packaging and refinement.

Do not use output as final load instructions without qualified review.


CONTENTS
--------

  Load Planner.exe   Application
  crate_data.xlsx    Crate list (replace with your export)
  load_plans/        Saved floor-plan images
  README.txt         This file


QUICK START
-----------

1. Place your Excel file here as crate_data.xlsx,
   or click Browse in the app to select another file.

2. Enter a trailer / load name (e.g. Load-01).
   This name appears on the plot and in the filename.

3. Use the default trailer preset or enter custom dimensions.

4. Click Run load plan.

5. Click Open latest plot, or Open load_plans folder.


TRAILER CONFIGURATION
---------------------

  Enter length, width, height, and maximum weight in the app,
  or use the default preset for quick demos.


EXCEL FORMAT
------------

Required columns:
  Asset Tag
  Gross Weight (kg)

Dimensions — either:
  Length (cm), Width (cm), Height (cm)
  — or —
  Size (cm)  as  length x width x height  (e.g. 147x131x257)


WHAT THE TOOL DOES
------------------

  - Reads crate sizes and weights from Excel
  - Pairs crates side-by-side when they fit across the trailer width
  - Places remaining crates alternating left/right on the walls (chessboard)
  - Loads from the cab end toward the doors; heavier items toward the cab
  - Keeps left/right weight balance within 10%
  - Saves a floor-plan PNG to load_plans/
  - Lists crates that need a second trailer


WHAT THE TOOL DOES NOT DO
-------------------------

  - Does not rotate crates
  - Does not stack crates vertically (2D floor plan only)
  - Does not guarantee the optimal or minimum number of trailers
  - Does not replace qualified human review of load plans


UPDATING DATA
-------------

Replace crate_data.xlsx with a new export (same column names).
No reinstall needed.


TROUBLESHOOTING
---------------

  Python was not found     Not required — use Load Planner.exe only
  Excel not found          Put crate_data.xlsx here or use Browse
  Plot did not open        Check the load_plans folder
  SmartScreen warning      Ask IT to allowlist Load Planner.exe


FOR DEVELOPERS
--------------

Rebuild this package from the main project folder:

  build_exe.bat

Full documentation: README.md and DEPLOY_WORK_PC.md in the source project.
