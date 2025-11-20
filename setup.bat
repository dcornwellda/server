@echo off
echo ============================================================
echo Remote Instrument Server - Setup Script
echo ============================================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or newer from https://www.python.org
    pause
    exit /b 1
)
echo.

echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages!
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Installation complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Find your Keithley address (see QUICKSTART.md)
echo 2. Run: python main.py
echo 3. Open http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
