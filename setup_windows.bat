@echo off
echo ====================================
echo   Binance Trader - Windows Setup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Check if yarn is installed
yarn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Yarn is not installed. Installing yarn globally...
    npm install -g yarn
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install yarn
        pause
        exit /b 1
    )
)

echo All prerequisites are installed!
echo.
echo Installing project dependencies...
echo.

REM Create virtual environment for backend
echo Creating Python virtual environment...
cd /d "%~dp0backend"
if not exist "venv" (
    echo Creating new virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install requirements
echo Installing Python dependencies...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment activation script not found
    pause
    exit /b 1
)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    echo Trying alternative installation...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Alternative installation also failed
        pause
        exit /b 1
    )
)

REM Install frontend dependencies
echo.
echo Installing Frontend dependencies...
cd /d "%~dp0frontend"
yarn install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

REM Create .env files if they don't exist
echo.
echo Setting up environment files...

cd /d "%~dp0backend"
if not exist ".env" (
    echo Creating backend .env file...
    echo MONGO_URL=mongodb://localhost:27017 > .env
    echo DB_NAME=binance_trader >> .env
)

cd /d "%~dp0frontend"
if not exist ".env" (
    echo Creating frontend .env file...
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > .env
)

echo.
echo ====================================
echo     Setup completed successfully!
echo ====================================
echo.
echo Next steps:
echo 1. Make sure MongoDB is running (install from https://mongodb.com if needed)
echo 2. Run start_app.bat to launch the application
echo.
pause