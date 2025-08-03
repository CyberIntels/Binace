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
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Install requirements
echo 📦 Installing requirements...
pip install -r backend\simple_requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    pause
    exit /b 1
)

echo ✅ Requirements installed
echo.

echo 🔥 Starting Simple Binance Trader Server...
echo 📊 Real crypto data from CoinGecko API
echo 🌐 Server will be available at http://localhost:8001
echo 📱 Frontend available at simple_frontend.html
echo.
echo Press Ctrl+C to stop
echo.

REM Change to backend directory and start server
cd backend
python simple_server.py

pause