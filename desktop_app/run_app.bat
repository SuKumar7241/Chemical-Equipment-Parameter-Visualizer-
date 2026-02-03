@echo off
echo Starting Dataset Analyzer Desktop Application...
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo Error: Please run this from the desktop_app directory
    pause
    exit /b 1
)

REM Run the application
python launch.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)