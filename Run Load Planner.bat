@echo off
title Trailer Load Planner
cd /d "%~dp0"

REM --- Option A: project virtual environment (development copy) ---
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" "%~dp0load_planner_gui.py"
    exit /b 0
)

REM --- Option B: Python installed on the PC (IT image) ---
where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw "%~dp0load_planner_gui.py"
    exit /b 0
)

where py >nul 2>&1
if %errorlevel%==0 (
    start "" py -3 "%~dp0load_planner_gui.py"
    exit /b 0
)

echo Python was not found on this PC.
echo Ask IT to install Python 3.10+ or use the standalone Load Planner.exe build.
echo.
pause
