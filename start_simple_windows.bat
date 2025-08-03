@echo off
title Binance Trader Simple Server
echo ===============================
echo 🚀 BINANCE TRADER - SIMPLE MODE
echo ===============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version
echo.

REM Check if we're in the right directory
if not exist "backend\simple_server.py" (
    echo ❌ Error: simple_server.py not found in backend directory
    echo Please run this script from the project root directory
    echo Current directory: %cd%
    echo.
    pause
    exit /b 1
)

REM Kill any existing server processes
echo 🛑 Stopping any existing server processes...
taskkill /f /im python.exe >nul 2>&1

REM Install requirements
echo 📦 Installing requirements...
pip install -r backend\simple_requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    echo Try running: python -m pip install --upgrade pip
    echo.
    pause
    exit /b 1
)

echo ✅ Requirements installed successfully
echo.

echo 🔥 Starting Simple Binance Trader Server...
echo.
echo 📊 Features:
echo    • Real crypto data from CoinGecko API
echo    • 6 trading pairs: BTC, ETH, BNB, ADA, SOL, DOT
echo    • Real-time price updates via WebSocket
echo    • Buy/Sell trading simulation
echo    • Emergency sell functionality
echo.
echo 🌐 Server will be available at: http://localhost:8001
echo 📱 Frontend files:
echo    • simple_frontend_local.html (for Windows)
echo    • simple_frontend.html (for cloud deployment)
echo.
echo ⚡ Press Ctrl+C to stop the server
echo ===============================
echo.

REM Change to backend directory and start server
cd backend
echo Starting server...
python simple_server.py

echo.
echo Server stopped. Press any key to exit...
pause >nul