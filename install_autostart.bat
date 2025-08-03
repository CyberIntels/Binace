@echo off
echo ====================================
echo   Install Auto-startup on Boot
echo ====================================
echo.

set SCRIPT_DIR=%~dp0
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo This will add Binance Trader to Windows startup.
echo The application will start automatically when Windows boots.
echo.
echo Choose startup mode:
echo 1) Normal mode (shows console windows)
echo 2) Silent mode (runs in background) [RECOMMENDED]
echo 3) Cancel
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    copy "%SCRIPT_DIR%start_app.bat" "%STARTUP_FOLDER%\Binance Trader Startup.bat" >nul
    echo.
    echo ✓ Normal startup installed successfully!
    echo Application will start with console windows visible.
) else if "%choice%"=="2" (
    copy "%SCRIPT_DIR%start_app_silent.bat" "%STARTUP_FOLDER%\Binance Trader Startup.bat" >nul
    echo.
    echo ✓ Silent startup installed successfully!
    echo Application will start in background when Windows boots.
) else if "%choice%"=="3" (
    echo Operation cancelled.
    pause
    exit /b 0
) else (
    echo Invalid choice. Operation cancelled.
    pause
    exit /b 1
)

echo.
echo The application will now start automatically when Windows starts.
echo.
echo To remove auto-startup later:
echo 1) Go to: %STARTUP_FOLDER%
echo 2) Delete "Binance Trader Startup.bat"
echo.
echo or run: uninstall_autostart.bat
echo.
pause