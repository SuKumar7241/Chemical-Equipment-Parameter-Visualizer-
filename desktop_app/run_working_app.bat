@echo off
echo Starting Working Matplotlib Desktop App...
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Starting the matplotlib desktop application...
echo This version uses matplotlib with Agg backend and displays charts as images.
echo.

python working_matplotlib_app.py

if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)