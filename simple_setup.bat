@echo off
echo ====================================
echo   Binance Trader - Установка
echo ====================================
echo.

REM Check if we're in the right directory
if not exist "backend\server.py" (
    echo ❌ ОШИБКА: Неправильная папка!
    echo.
    echo Пожалуйста запустите этот файл из папки где есть:
    echo - папка backend\
    echo - папка frontend\
    echo.
    pause
    exit /b 1
)

echo Setting up Python backend...
cd backend

REM Clean up any existing venv
if exist "venv" (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

echo Creating new virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python is properly installed
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing backend dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)

cd ..

REM Check for Node.js and install frontend dependencies
echo.
echo Setting up Node.js frontend...
cd frontend

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found. Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

where yarn >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing yarn...
    npm install -g yarn
)

echo Installing frontend dependencies...
yarn install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend packages
    pause
    exit /b 1
)

cd ..

REM Create Windows-specific .env files
echo.
echo Creating configuration files...

if not exist "backend\.env" (
    echo MONGO_URL=mongodb://localhost:27017 > backend\.env
    echo DB_NAME=binance_trader >> backend\.env
    echo.Created backend\.env
)

if not exist "frontend\.env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env
    echo.Created frontend\.env
)

echo.
echo ====================================
echo     Setup completed successfully!
echo ====================================
echo.
echo To start the application:
echo   1. Run: start_app.bat
echo   2. Or run: start_app_silent.bat (background mode)
echo.
echo The app will open at: http://localhost:3000
echo.
pause