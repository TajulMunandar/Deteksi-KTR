@echo off
echo ============================================
echo   Citra KTR Map - Monitoring Pelanggaran Merokok
echo   Web App Server Starter
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.x from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment (venv)
    set PYTHON_EXE=venv\Scripts\python.exe
) else (
    echo [WARNING] Virtual environment not found
    echo [INFO] Using system Python
    set PYTHON_EXE=python
)
echo.

REM Check if required files exist
if not exist "index.html" (
    echo [ERROR] index.html not found!
    pause
    exit /b 1
)

if not exist "style.css" (
    echo [ERROR] style.css not found!
    pause
    exit /b 1
)

if not exist "script.js" (
    echo [ERROR] script.js not found!
    pause
    exit /b 1
)

echo [OK] All required files found
echo.

REM Start the server
echo Starting server...
echo.
echo ============================================
echo   Server will open in your browser
echo   Press Ctrl+C to stop the server
echo   Server URL: http://localhost:5000
echo ============================================
echo.

%PYTHON_EXE% server.py
