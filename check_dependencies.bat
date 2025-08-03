@echo off
echo ====================================
echo   Binance Trader - Dependencies Check
echo ====================================
echo.

set "all_ok=1"

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo ✓ %%i
    
    REM Check pip
    pip --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=1,2" %%i in ('pip --version 2^>^&1') do echo ✓ pip %%j
    ) else (
        echo ✗ pip not found
        set "all_ok=0"
    )
) else (
    echo ✗ Python not found or not in PATH
    set "all_ok=0"
)

echo.
REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo ✓ Node.js %%i
    
    REM Check npm
    npm --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=*" %%i in ('npm --version 2^>^&1') do echo ✓ npm %%i
    ) else (
        echo ✗ npm not found
        set "all_ok=0"
    )
) else (
    echo ✗ Node.js not found or not in PATH
    set "all_ok=0"
)

echo.
REM Check Yarn
echo Checking Yarn...
yarn --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('yarn --version 2^>^&1') do echo ✓ Yarn %%i
) else (
    echo ⚠ Yarn not found (will be installed automatically)
)

echo.
REM Check MongoDB (optional)
echo Checking MongoDB (optional)...
mongod --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ MongoDB is installed
) else (
    echo ⚠ MongoDB not found (app will use fallback data)
)

echo.
REM Check ports
echo Checking port availability...
netstat -an | find "LISTENING" | find ":8001 " >nul
if %errorlevel% equ 0 (
    echo ⚠ Port 8001 is in use
) else (
    echo ✓ Port 8001 is available
)

netstat -an | find "LISTENING" | find ":3000 " >nul
if %errorlevel% equ 0 (
    echo ⚠ Port 3000 is in use
) else (
    echo ✓ Port 3000 is available
)

echo.
REM Check project files
echo Checking project files...
if exist "backend\server.py" (
    echo ✓ Backend files found
) else (
    echo ✗ Backend files missing
    set "all_ok=0"
)

if exist "frontend\package.json" (
    echo ✓ Frontend files found
) else (
    echo ✗ Frontend files missing
    set "all_ok=0"
)

if exist "backend\requirements.txt" (
    echo ✓ Python requirements file found
) else (
    echo ✗ Python requirements file missing
    set "all_ok=0"
)

echo.
echo ====================================
if "%all_ok%"=="1" (
    echo      All dependencies are OK! ✓
    echo ====================================
    echo.
    echo You can now run:
    echo   setup_windows.bat  - to install project dependencies
    echo   start_app.bat      - to start the application
) else (
    echo    Some dependencies are missing! ✗
    echo ====================================
    echo.
    echo Please install missing dependencies:
    echo   Python 3.8+: https://python.org
    echo   Node.js 16+: https://nodejs.org
    echo.
    echo Then run setup_windows.bat
)
echo.
pause