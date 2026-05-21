@echo off
REM Build a standalone Load Planner.exe (run once on a dev machine, then copy the folder to work PCs).
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Create the venv first: python -m venv .venv
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --onefile --windowed ^
  --name "Load Planner" ^
  --paths "%~dp0" ^
  "%~dp0load_planner_gui.py"

echo.
echo Build finished. Copy this folder to work PCs:
echo   dist\Load Planner.exe
echo   crate_data.xlsx
echo   load_plans\   (empty folder is fine)
echo.
pause
