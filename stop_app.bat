@echo off
echo.
echo ====================================
echo   Stopping Binance Trader...
echo ====================================
echo.

REM Kill Node.js processes (frontend)
echo Stopping frontend server...
taskkill /f /im node.exe >nul 2>&1

REM Kill Python processes (backend)
echo Stopping backend server...
taskkill /f /im python.exe >nul 2>&1

REM Kill yarn processes
echo Stopping yarn processes...
taskkill /f /im yarn.exe >nul 2>&1

echo.
echo Application stopped successfully!
echo.
pause