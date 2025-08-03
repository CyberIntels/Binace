@echo off
echo Проверяем Node.js...

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ Node.js не установлен!
    echo.
    echo Пожалуйста:
    echo 1. Идите на https://nodejs.org
    echo 2. Скачайте LTS версию
    echo 3. Установите (просто нажимайте "Далее")
    echo 4. Перезапустите командную строку
    echo 5. Запустите simple_setup.bat
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo ✅ Node.js установлен: %%i
    echo.
    echo Теперь можете запустить:
    echo    simple_setup.bat
    echo.
    pause
)