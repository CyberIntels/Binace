# Binance Trader - Windows Installation Guide

## 🚀 Quick Start

### Method 1: Simple Batch Files (Recommended for beginners)

1. **First Time Setup:**
   ```cmd
   setup_windows.bat
   ```

2. **Start Application:**
   ```cmd
   start_app.bat
   ```

3. **Start Application (Silent):**
   ```cmd
   start_app_silent.bat
   ```

4. **Stop Application:**
   ```cmd
   stop_app.bat
   ```

### Method 2: PowerShell (Advanced users)

```powershell
powershell -ExecutionPolicy Bypass -File "Start-BinanceTrader.ps1"
```

---

## 📋 Prerequisites

Before running the application, make sure you have:

1. **Python 3.8+**
   - Download from: https://python.org
   - ⚠️ **Important**: Check "Add Python to PATH" during installation

2. **Node.js 16+**
   - Download from: https://nodejs.org
   - This will also install npm automatically

3. **MongoDB** (Optional - app has fallback data)
   - Download from: https://mongodb.com
   - Or use MongoDB Atlas (cloud)

---

## 🛠️ Installation Steps

### Step 1: Download/Clone the Project
```cmd
# If you have git installed:
git clone <repository-url>
cd binance-trader

# Or download and extract ZIP file
```

### Step 2: Run Setup
```cmd
setup_windows.bat
```

This will:
- Check all prerequisites
- Install Python dependencies in virtual environment
- Install Node.js dependencies with Yarn
- Create necessary .env files

### Step 3: Start Application
```cmd
start_app.bat
```

This will:
- Start backend server on port 8001
- Start frontend server on port 3000
- Automatically open browser to http://localhost:3000

---

## 🎯 Usage

### Starting the Application

**Option A - With Console Windows (Default):**
```cmd
start_app.bat
```
- Shows backend and frontend logs in separate windows
- Good for debugging

**Option B - Silent Mode:**
```cmd
start_app_silent.bat
```
- Runs servers in background
- Only opens the browser
- Cleaner experience

**Option C - PowerShell (Advanced):**
```powershell
powershell -ExecutionPolicy Bypass -File "Start-BinanceTrader.ps1"
```
- Advanced logging and error handling
- Better status feedback

### Stopping the Application

```cmd
stop_app.bat
```
- Stops all backend and frontend processes
- Clean shutdown

---

## 🔧 Configuration

### Backend Configuration (`backend/.env`)
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=binance_trader
```

### Frontend Configuration (`frontend/.env`)
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

### AI Trading Settings
1. Open http://localhost:3000
2. Go to Settings → AI tab
3. Enter your OpenAI API key
4. Enable AI signals
5. Select your preferred model:
   - GPT-4o (Recommended)
   - GPT-4.1
   - Claude Sonnet
   - Gemini 2.0 Flash

---

## 🌐 Accessing the Application

- **Main Application**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs (FastAPI auto-docs)

---

## 🐛 Troubleshooting

### Common Issues:

1. **"Python is not recognized"**
   - Reinstall Python and check "Add to PATH"
   - Or manually add Python to PATH

2. **"Node is not recognized"**
   - Install Node.js from nodejs.org
   - Restart command prompt after installation

3. **Port already in use**
   - Run `stop_app.bat` first
   - Or manually kill processes:
     ```cmd
     taskkill /f /im python.exe
     taskkill /f /im node.exe
     ```

4. **Frontend won't start**
   - Delete `node_modules` in frontend folder
   - Run `yarn install` again
   - Make sure yarn is installed: `npm install -g yarn`

5. **Backend errors**
   - Check if all dependencies installed: `pip install -r requirements.txt`
   - Make sure virtual environment is activated
   - Check MongoDB connection

6. **Browser doesn't open**
   - Manually go to: http://localhost:3000
   - Check if both servers are running
   - Check firewall settings

### Log Files:
- Backend logs: Check backend console window
- Frontend logs: Check frontend console window
- Browser logs: Press F12 and check Console tab

---

## 🚀 Auto-startup on Windows Boot (Optional)

### Method 1: Startup Folder
1. Press `Win + R`, type `shell:startup`, press Enter
2. Copy `start_app_silent.bat` to this folder
3. Application will start automatically when Windows boots

### Method 2: Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "When computer starts"
4. Set action to start `start_app_silent.bat`

---

## 📊 Features

- **Real-time Crypto Prices** from CoinGecko API
- **AI Trading Signals** using OpenAI/Claude/Gemini
- **WebSocket Real-time Updates**
- **Spot & Futures Trading Interface**
- **Customizable Settings**
- **Trading History**
- **Emergency Stop Function**

---

## 🔐 Security Notes

- Never share your API keys
- API keys are stored locally in .env files
- Backend API is only accessible from localhost by default
- Use HTTPS in production

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check console logs for error messages
4. Ensure ports 3000 and 8001 are available

---

## 🎮 Quick Command Reference

```cmd
# Setup (run once)
setup_windows.bat

# Start with console windows
start_app.bat

# Start in background
start_app_silent.bat

# Stop everything
stop_app.bat

# PowerShell start
powershell -ExecutionPolicy Bypass -File "Start-BinanceTrader.ps1"
```

Happy Trading! 🚀📈