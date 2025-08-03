@echo off
title Binance Trader - Final Start
color 0A

echo.
echo ====================================
echo   🚀 Binance Trader - Запуск
echo ====================================
echo.

echo Проверяем установку...

if not exist "backend\venv\Scripts\python.exe" (
    echo ❌ Сначала запустите: one_click_fix.bat
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo ❌ Сначала запустите: one_click_fix.bat  
    pause
    exit /b 1
)

echo ✅ Все готово!
echo.

echo Запускаем Backend...
cd backend
start "💰 Binance Backend" cmd /k "venv\Scripts\activate.bat && python server.py"

timeout /t 3 /nobreak >nul

echo Запускаем Frontend...  
cd ..\frontend
start "🌐 Binance Frontend" cmd /k "npm start"

echo.
echo ⏰ Ожидание запуска (20 сек)...
timeout /t 20 /nobreak >nul

echo 🌐 Открываем браузер...
start http://localhost:3000

echo.
echo ========================================
echo     🎉 ПРИЛОЖЕНИЕ ЗАПУЩЕНО!
echo ========================================
echo.
echo 🌐 Веб-интерфейс: http://localhost:3000
echo 🔧 Backend API:   http://localhost:8001
echo.
echo ⚠️ НЕ ЗАКРЫВАЙТЕ окна Backend и Frontend!
echo.
echo Для остановки используйте: stop_app.bat
echo.
pause