@echo off
echo Starting Dataset Analyzer - Fixed Version
echo This version removes matplotlib to avoid Qt5 backend hanging issues
echo.

python desktop_app/complete_app_no_matplotlib.py

echo.
echo App closed.
pause