@echo off
TITLE VibeParser - Document Text Extraction System
echo ==========================================
echo Starting VibeParser Application
echo ==========================================
echo.
echo Please wait while the application starts...
echo.
echo The application will open in your default browser.
echo If it doesn't open automatically, navigate to http://localhost:8501
echo.
echo To stop the application, close this window or press Ctrl+C
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and make sure it's added to your PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting VibeParser...
echo.
streamlit run app.py

pause