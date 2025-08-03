@echo off
title Binance Trader (Простая версия)
color 0A

echo.
echo ====================================
echo   Binance Trader - Запуск (npm)
echo ====================================
echo.

REM Check if backend setup is done
if not exist "backend\venv\Scripts\python.exe" (
    echo.
    echo ❌ Backend не настроен!
    echo.
    echo Запустите сначала:
    echo    simple_setup.bat
    echo.
    pause
    exit /b 1
)

REM Check if frontend is fixed
if not exist "frontend\node_modules" (
    echo.
    echo ❌ Frontend не настроен!
    echo.
    echo Запустите сначала:
    echo    simple_frontend_fix.bat
    echo.
    pause
    exit /b 1
)

echo Starting backend server...
cd backend
start "Backend" cmd /k "venv\Scripts\activate.bat && python server.py"

timeout /t 4 /nobreak >nul

cd ..\frontend
echo Starting frontend server...
start "Frontend" cmd /k "npm start"

echo Ожидание запуска серверов...
timeout /t 15 /nobreak >nul

echo Открываем браузер...
start http://localhost:3000

echo.
echo ====================================
echo        Готово! ✅
echo ====================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8001
echo.
echo Два окна открылось - не закрывайте их!
echo.
pause