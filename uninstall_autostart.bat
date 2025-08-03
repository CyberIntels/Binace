@echo off
echo ====================================
echo   Remove Auto-startup from Boot
echo ====================================
echo.

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

if exist "%STARTUP_FOLDER%\Binance Trader Startup.bat" (
    del "%STARTUP_FOLDER%\Binance Trader Startup.bat"
    echo ✓ Auto-startup removed successfully!
    echo Binance Trader will no longer start with Windows.
) else (
    echo ⚠ Auto-startup was not installed or already removed.
)

echo.
pause