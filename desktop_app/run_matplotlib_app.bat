@echo off
echo Starting Dataset Analysis Platform with Matplotlib...
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
echo Checking required packages...
python -c "import PyQt5; print('PyQt5: OK')" 2>nul || (
    echo ERROR: PyQt5 not installed. Run: pip install PyQt5==5.15.9
    pause
    exit /b 1
)

python -c "import matplotlib; print('matplotlib: OK')" 2>nul || (
    echo ERROR: matplotlib not installed. Run: pip install matplotlib==3.7.1
    pause
    exit /b 1
)

python -c "import requests; print('requests: OK')" 2>nul || (
    echo ERROR: requests not installed. Run: pip install requests==2.31.0
    pause
    exit /b 1
)

python -c "import pandas; print('pandas: OK')" 2>nul || (
    echo ERROR: pandas not installed. Run: pip install pandas==2.0.3
    pause
    exit /b 1
)

python -c "import numpy; print('numpy: OK')" 2>nul || (
    echo ERROR: numpy not installed. Run: pip install numpy==1.24.3
    pause
    exit /b 1
)

echo.
echo All dependencies are installed!
echo Starting application...
echo.

python matplotlib_app.py

if errorlevel 1 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
)