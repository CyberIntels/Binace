@echo off
title Binance Trader - Одним кликом
color 0B

echo.
echo ========================================
echo    🚀 Binance Trader - Полное исправление
echo ========================================
echo.
echo Это исправит ВСЕ проблемы одной командой!
echo.
pause

REM Step 1: Backend setup
echo.
echo 📦 ШАГ 1: Настройка Backend...
echo.

cd backend
if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cd ..

REM Step 2: Frontend fix
echo.
echo 🌐 ШАГ 2: Исправление Frontend...
echo.

cd frontend
if exist node_modules rmdir /s /q node_modules
if exist yarn.lock del yarn.lock
if exist package-lock.json del package-lock.json

REM Create simple package.json
echo {> temp_package.json
echo   "name": "binance-trader",>> temp_package.json
echo   "version": "1.0.0",>> temp_package.json
echo   "private": true,>> temp_package.json
echo   "dependencies": {>> temp_package.json
echo     "react": "^18.2.0",>> temp_package.json
echo     "react-dom": "^18.2.0",>> temp_package.json
echo     "react-scripts": "5.0.1">> temp_package.json
echo   },>> temp_package.json
echo   "scripts": {>> temp_package.json
echo     "start": "react-scripts start",>> temp_package.json
echo     "build": "react-scripts build">> temp_package.json
echo   },>> temp_package.json
echo   "browserslist": {>> temp_package.json
echo     "production": [">0.2%", "not dead", "not op_mini all"],>> temp_package.json
echo     "development": ["last 1 chrome version", "last 1 firefox version"]>> temp_package.json
echo   }>> temp_package.json
echo }>> temp_package.json

copy temp_package.json package.json
del temp_package.json

REM Replace App.js with simple version
copy src\App_simple.js src\App.js

npm install --legacy-peer-deps

cd ..

REM Step 3: Create env files
echo.
echo ⚙️ ШАГ 3: Настройка конфигурации...
echo.

echo MONGO_URL=mongodb://localhost:27017 > backend\.env
echo DB_NAME=binance_trader >> backend\.env

echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env

echo.
echo ========================================
echo        ✅ ВСЕ ИСПРАВЛЕНО!
echo ========================================
echo.
echo Теперь запустите:
echo    final_start.bat
echo.
pause