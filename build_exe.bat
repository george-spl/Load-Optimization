@echo off
REM Build Load Planner.exe and copy into "Load Planner Package" for work PCs.
cd /d "%~dp0"
set "ROOT=%CD%"

if not exist "%ROOT%\.venv\Scripts\python.exe" (
    echo Create the venv first: python -m venv .venv
    echo .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

call "%ROOT%\.venv\Scripts\activate.bat"
pip install -r requirements.txt pyinstaller -q

pyinstaller --noconfirm --onefile --windowed ^
  --name "Load Planner" ^
  --paths "%ROOT%" ^
  "%ROOT%\load_planner_gui.py"

if errorlevel 1 (
    echo.
    echo Build FAILED. Load Planner.exe was not created.
    pause
    exit /b 1
)

if not exist "%ROOT%\dist\Load Planner.exe" (
    echo.
    echo Build FAILED: dist\Load Planner.exe not found.
    pause
    exit /b 1
)

set "PKG=%ROOT%\Load Planner Package"
mkdir "%PKG%" 2>nul
mkdir "%PKG%\load_plans" 2>nul
copy /Y "%ROOT%\dist\Load Planner.exe" "%PKG%\"
if exist "%ROOT%\crate_data.xlsx" copy /Y "%ROOT%\crate_data.xlsx" "%PKG%\"

echo.
echo Build succeeded.
echo Ready to copy to work PCs:
echo   %PKG%
echo.
echo   Load Planner.exe
echo   crate_data.xlsx
echo   load_plans\
echo.
pause
