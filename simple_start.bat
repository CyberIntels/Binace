@echo off
title Binance Trader Launcher
color 0A

echo.
echo ====================================
echo     Binance Trader - Starting...
echo ====================================
echo.

REM Check if we're in the right directory
if not exist "backend\server.py" (
    echo ERROR: Please run this script from the Binance Trader root directory
    pause
    exit /b 1
)

REM Check if setup was run
if not exist "backend\venv\Scripts\python.exe" (
    echo.
    echo ❌ ERROR: Приложение еще не настроено!
    echo.
    echo Пожалуйста, сначала запустите:
    echo    simple_setup.bat
    echo.
    echo А затем повторите:  
    echo    simple_start.bat
    echo.
    pause
    exit /b 1
)

echo Starting backend server...
cd backend
start "Backend - Binance Trader" cmd /k "venv\Scripts\activate.bat && python server.py"

REM Wait for backend to start
timeout /t 4 /nobreak >nul

cd ..\frontend
echo Starting frontend server...
start "Frontend - Binance Trader" cmd /k "yarn start"

REM Wait for frontend to load
echo Waiting for servers to start...
timeout /t 12 /nobreak >nul

echo Opening browser...
start http://localhost:3000

echo.
echo ====================================
echo   Application started successfully!
echo ====================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8001
echo.
echo Two windows opened - don't close them!
echo This window can be closed safely.
echo.
pause