@echo off
title Binance Trader - Startup
color 0A

echo.
echo ====================================
echo     Binance Trader - Starting...
echo ====================================
echo.

REM Change to the directory where the batch file is located
cd /d "%~dp0"

REM Check if MongoDB is running
echo Checking MongoDB connection...
timeout /t 2 /nobreak >nul

REM Start backend server
echo Starting backend server on port 8001...
cd /d "%~dp0backend"
start "Binance Trader Backend" cmd /k "call venv\Scripts\activate && python server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend development server
echo Starting frontend server on port 3000...
cd /d "%~dp0frontend"
start "Binance Trader Frontend" cmd /k "yarn start"

REM Wait for frontend to start
echo Waiting for application to start...
timeout /t 8 /nobreak >nul

REM Open application in default browser
echo Opening application in browser...
start http://localhost:3000

echo.
echo ====================================
echo   Application started successfully!
echo ====================================
echo.
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo Press any key to keep this window open or close it manually.
echo Both servers will continue running in separate windows.
echo.
pause >nul