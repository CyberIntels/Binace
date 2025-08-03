@echo off
echo Creating desktop shortcuts for Binance Trader...

set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop

REM Create Start Application shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\🚀 Start Binance Trader.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%SCRIPT_DIR%start_app.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Start Binance Trader Application" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,137" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"
cscript "%TEMP%\CreateShortcut.vbs" >nul

REM Create Start Silent shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut2.vbs"
echo sLinkFile = "%DESKTOP%\⚡ Start Binance Trader (Silent).lnk" >> "%TEMP%\CreateShortcut2.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut2.vbs"
echo oLink.TargetPath = "%SCRIPT_DIR%start_app_silent.bat" >> "%TEMP%\CreateShortcut2.vbs"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\CreateShortcut2.vbs"
echo oLink.Description = "Start Binance Trader Application (Silent Mode)" >> "%TEMP%\CreateShortcut2.vbs"
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,25" >> "%TEMP%\CreateShortcut2.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut2.vbs"
cscript "%TEMP%\CreateShortcut2.vbs" >nul

REM Create Stop Application shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut3.vbs"
echo sLinkFile = "%DESKTOP%\⏹️ Stop Binance Trader.lnk" >> "%TEMP%\CreateShortcut3.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut3.vbs"
echo oLink.TargetPath = "%SCRIPT_DIR%stop_app.bat" >> "%TEMP%\CreateShortcut3.vbs"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\CreateShortcut3.vbs"
echo oLink.Description = "Stop Binance Trader Application" >> "%TEMP%\CreateShortcut3.vbs"
echo oLink.IconLocation = "%SystemRoot%\System32\shell32.dll,132" >> "%TEMP%\CreateShortcut3.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut3.vbs"
cscript "%TEMP%\CreateShortcut3.vbs" >nul

REM Clean up
del "%TEMP%\CreateShortcut.vbs" >nul 2>&1
del "%TEMP%\CreateShortcut2.vbs" >nul 2>&1
del "%TEMP%\CreateShortcut3.vbs" >nul 2>&1

echo.
echo ✓ Desktop shortcuts created successfully!
echo.
echo Created shortcuts:
echo   🚀 Start Binance Trader
echo   ⚡ Start Binance Trader (Silent)
echo   ⏹️ Stop Binance Trader
echo.
pause