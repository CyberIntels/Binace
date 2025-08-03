@echo off
REM Silent startup version - no console windows, just opens browser

REM Change to the directory where the batch file is located
cd /d "%~dp0"

REM Start backend server (hidden)
cd /d "%~dp0backend"
start /min "" cmd /c "call venv\Scripts\activate && python server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul 2>&1

REM Start frontend development server (hidden)
cd /d "%~dp0frontend" 
start /min "" cmd /c "yarn start"

REM Wait for servers to start
timeout /t 10 /nobreak >nul 2>&1

REM Open application in browser
start http://localhost:3000

REM Exit this script
exit