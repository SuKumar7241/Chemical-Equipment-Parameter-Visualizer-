@echo off
echo === Dataset Analyzer - Enhanced Version ===
echo Starting enhanced desktop application...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import PyQt5, matplotlib, requests, numpy" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Missing required packages
    echo Installing required packages...
    pip install PyQt5 matplotlib requests numpy pandas
    if errorlevel 1 (
        echo Failed to install packages
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.

REM Start the enhanced application
echo Launching enhanced desktop application...
python enhanced_app.py

pause