@echo off
title Binance Trader - Master Windows Installer
color 0B

echo.
echo ========================================
echo    🚀 BINANCE TRADER - WINDOWS SETUP
echo ========================================
echo.
echo Welcome to the Binance Trader installation wizard!
echo This will set up everything needed to run the app on Windows.
echo.
pause

REM Step 1: Check dependencies
echo.
echo ========================================
echo    📋 STEP 1: CHECKING DEPENDENCIES
echo ========================================
echo.
call check_dependencies.bat

echo.
echo Press any key to continue with installation...
pause >nul

REM Step 2: Install project dependencies
echo.
echo ========================================
echo    📦 STEP 2: INSTALLING PROJECT
echo ========================================
echo.
call setup_windows.bat

echo.
echo Press any key to continue...
pause >nul

REM Step 3: Create shortcuts
echo.
echo ========================================
echo    🔗 STEP 3: CREATING SHORTCUTS
echo ========================================
echo.
echo Do you want to create desktop shortcuts?
set /p create_shortcuts="Create desktop shortcuts? (y/n): "
if /i "%create_shortcuts%"=="y" (
    call create_desktop_shortcuts.bat
)

REM Step 4: Auto-startup option
echo.
echo ========================================
echo    ⚡ STEP 4: AUTO-STARTUP (OPTIONAL)
echo ========================================
echo.
echo Do you want to enable auto-startup when Windows boots?
set /p enable_autostart="Enable auto-startup? (y/n): "
if /i "%enable_autostart%"=="y" (
    call install_autostart.bat
)

REM Step 5: Test run
echo.
echo ========================================
echo    🧪 STEP 5: TEST RUN
echo ========================================
echo.
echo Installation complete! Would you like to test the application now?
set /p test_run="Start Binance Trader now? (y/n): "
if /i "%test_run%"=="y" (
    echo Starting application in 3 seconds...
    timeout /t 3 /nobreak >nul
    call start_app.bat
) else (
    echo.
    echo ========================================
    echo       🎉 INSTALLATION COMPLETE!
    echo ========================================
    echo.
    echo To start the application later, run:
    echo   • start_app.bat           (with console windows)
    echo   • start_app_silent.bat    (background mode)
    echo   • Or use the desktop shortcuts (if created)
    echo.
    echo To stop the application:
    echo   • stop_app.bat
    echo.
    echo Documentation: README_WINDOWS.md
    echo.
    pause
)