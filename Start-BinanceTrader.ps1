# PowerShell script for starting Binance Trader
# Run this script with: powershell -ExecutionPolicy Bypass -File "Start-BinanceTrader.ps1"

Write-Host "=====================================" -ForegroundColor Green
Write-Host "   Binance Trader - PowerShell Start " -ForegroundColor Green  
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Function to check if a port is in use
function Test-Port {
    param([int]$Port)
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Yarn
try {
    $yarnVersion = yarn --version 2>&1
    Write-Host "✓ Yarn: $yarnVersion" -ForegroundColor Green
}
catch {
    Write-Host "⚠ Yarn not found. Installing yarn globally..." -ForegroundColor Yellow
    npm install -g yarn
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install yarn" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Starting application servers..." -ForegroundColor Yellow

# Check if servers are already running
if (Test-Port 8001) {
    Write-Host "⚠ Backend server already running on port 8001" -ForegroundColor Yellow
} else {
    Write-Host "Starting backend server..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\backend"
    
    # Start backend in new PowerShell window
    $backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {Set-Location '$ScriptDir\backend'; .\venv\Scripts\Activate.ps1; python server.py}" -WindowStyle Normal -PassThru
    
    # Wait for backend to start
    $timeout = 10
    $elapsed = 0
    while (-not (Test-Port 8001) -and $elapsed -lt $timeout) {
        Start-Sleep 1
        $elapsed++
        Write-Host "." -NoNewline -ForegroundColor Cyan
    }
    Write-Host ""
    
    if (Test-Port 8001) {
        Write-Host "✓ Backend server started successfully on port 8001" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to start backend server" -ForegroundColor Red
    }
}

if (Test-Port 3000) {
    Write-Host "⚠ Frontend server already running on port 3000" -ForegroundColor Yellow
} else {
    Write-Host "Starting frontend server..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\frontend"
    
    # Start frontend in new PowerShell window
    $frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {Set-Location '$ScriptDir\frontend'; yarn start}" -WindowStyle Normal -PassThru
    
    # Wait for frontend to start
    $timeout = 20
    $elapsed = 0
    while (-not (Test-Port 3000) -and $elapsed -lt $timeout) {
        Start-Sleep 1
        $elapsed++
        Write-Host "." -NoNewline -ForegroundColor Cyan
    }
    Write-Host ""
    
    if (Test-Port 3000) {
        Write-Host "✓ Frontend server started successfully on port 3000" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to start frontend server" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Opening application in browser..." -ForegroundColor Yellow
Start-Sleep 2
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "   Application started successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8001" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Application is now running in separate windows." -ForegroundColor Yellow
Write-Host "Press Enter to exit this setup window..." -ForegroundColor Yellow
Read-Host