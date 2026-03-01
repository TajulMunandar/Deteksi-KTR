@echo off
echo ============================================
echo   Citra KTR Map - Setup Virtual Environment
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if venv already exists
if exist "venv" (
    echo [INFO] Virtual environment already exists
    echo.
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [INFO] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo To run the application, use run.bat
echo Or manually: venv\Scripts\python.exe server.py
echo.
pause
