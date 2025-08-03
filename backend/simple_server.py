from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import json
import random
import time
import requests
from datetime import datetime, timedelta
import uuid
from typing import Optional, List
import os

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize data on startup"""
    await fetch_crypto_prices()
    print("🚀 Simple Binance Trader API started!")
    yield
    print("🔥 Simple Binance Trader API stopped!")

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NO MONGODB - just in-memory storage
CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT"]

# Global data store
CRYPTO_PAIRS = {}
last_update = 0
active_trades = []
settings = {
    "trade_amount": 500,
    "take_profit": 10,
    "stop_loss": 3
}

async def fetch_crypto_prices():
    """Fetch real prices from CoinGecko API"""
    global CRYPTO_PAIRS, last_update
    
    try:
        coin_mapping = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum", 
            "BNBUSDT": "binancecoin",
            "ADAUSDT": "cardano",
            "SOLUSDT": "solana",
            "DOTUSDT": "polkadot"
        }
        
        coin_ids = ",".join(coin_mapping.values())
        response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true", 
            timeout=10
        )
        
        if response.status_code == 200:
            price_data = response.json()
        else:
            print("Failed to fetch prices, using mock data")
            return init_mock_data()
        
        for symbol, coin_id in coin_mapping.items():
            if coin_id in price_data:
                coin_data = price_data[coin_id]
                base = symbol.replace('USDT', '')
                display_symbol = f"{base}/USDT"
                
                current_price = coin_data['usd']
                price_change = coin_data.get('usd_24h_change', 0)
                volume = coin_data.get('usd_24h_vol', 0)
                
                high_24h = current_price * (1 + abs(price_change) / 100) if price_change > 0 else current_price * 1.02
                low_24h = current_price * (1 - abs(price_change) / 100) if price_change < 0 else current_price * 0.98
                
                CRYPTO_PAIRS[symbol] = {
                    "symbol": display_symbol,
                    "price": current_price,
                    "change": price_change,
                    "volume": volume,
                    "high24h": high_24h,
                    "low24h": low_24h,
                    "lastUpdate": datetime.now().isoformat()
                }
        
        last_update = time.time()
        print(f"✅ Updated prices from CoinGecko for {len(CRYPTO_PAIRS)} pairs")
        return True
        
    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        return init_mock_data()

def init_mock_data():
    """Initialize with mock data if API fails"""
    global CRYPTO_PAIRS
    
    CRYPTO_PAIRS = {
        "BTCUSDT": {"symbol": "BTC/USDT", "price": 43251.50, "change": 2.45, "volume": 125000000, "high24h": 44100.00, "low24h": 42800.00, "lastUpdate": datetime.now().isoformat()},
        "ETHUSDT": {"symbol": "ETH/USDT", "price": 2651.75, "change": -1.23, "volume": 89000000, "high24h": 2720.50, "low24h": 2580.25, "lastUpdate": datetime.now().isoformat()},
        "BNBUSDT": {"symbol": "BNB/USDT", "price": 315.20, "change": 0.85, "volume": 45000000, "high24h": 325.80, "low24h": 308.90, "lastUpdate": datetime.now().isoformat()},
        "ADAUSDT": {"symbol": "ADA/USDT", "price": 0.4856, "change": 3.21, "volume": 28000000, "high24h": 0.5120, "low24h": 0.4650, "lastUpdate": datetime.now().isoformat()},
        "SOLUSDT": {"symbol": "SOL/USDT", "price": 98.45, "change": -2.10, "volume": 67000000, "high24h": 105.20, "low24h": 95.80, "lastUpdate": datetime.now().isoformat()},
        "DOTUSDT": {"symbol": "DOT/USDT", "price": 7.85, "change": 1.45, "volume": 23000000, "high24h": 8.15, "low24h": 7.60, "lastUpdate": datetime.now().isoformat()}
    }
    print("✅ Initialized with mock data")
    return True

# Initialize with data - will be called on startup

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(data))
            except:
                pass

manager = ConnectionManager()

# Simple models
class TradeOrder(BaseModel):
    id: str
    pair: str
    side: str
    amount: float
    price: float
    timestamp: datetime
    status: str = "filled"


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/pairs")
async def get_crypto_pairs():
    if not CRYPTO_PAIRS:
        await fetch_crypto_prices()
    return {"pairs": CRYPTO_PAIRS}

@app.post("/api/refresh-prices")
async def refresh_prices():
    success = await fetch_crypto_prices()
    if success:
        await manager.broadcast({"type": "price_update", "data": CRYPTO_PAIRS})
        return {"status": "success", "message": "Prices updated"}
    else:
        return JSONResponse(status_code=500, content={"error": "Failed to update prices"})

@app.get("/api/settings")
async def get_settings():
    return settings

@app.post("/api/settings")
async def update_settings(new_settings: dict):
    global settings
    settings.update(new_settings)
    return {"status": "updated"}

@app.post("/api/trade/{pair}")
async def execute_trade(pair: str, side: str):
    global active_trades
    
    if pair not in CRYPTO_PAIRS:
        return JSONResponse(status_code=404, content={"error": "Pair not found"})
    
    current_price = CRYPTO_PAIRS[pair]["price"]
    trade_id = str(uuid.uuid4())
    
    # Simulate slight slippage
    slippage = random.uniform(-0.001, 0.001)
    execution_price = current_price * (1 + slippage)
    
    trade = {
        "id": trade_id,
        "pair": pair,
        "side": side,
        "amount": settings["trade_amount"],
        "price": execution_price,
        "timestamp": datetime.now().isoformat(),
        "status": "filled"
    }
    
    active_trades.insert(0, trade)
    
    # Keep only last 20 trades
    if len(active_trades) > 20:
        active_trades = active_trades[:20]
    
    await manager.broadcast({"type": "trade_executed", "trade": trade})
    
    return {"status": "success", "trade": trade}

@app.post("/api/emergency-sell")
async def emergency_sell():
    """Close all positions immediately"""
    global active_trades
    closed_trades = []
    
    for trade in active_trades:
        if trade["side"] == "BUY":
            close_trade = {
                "id": str(uuid.uuid4()),
                "pair": trade["pair"],
                "side": "SELL",
                "amount": trade["amount"],
                "price": CRYPTO_PAIRS[trade["pair"]]["price"],
                "timestamp": datetime.now().isoformat(),
                "status": "emergency_close"
            }
            closed_trades.append(close_trade)
    
    # Add emergency sells to trades list
    active_trades = closed_trades + active_trades
    
    await manager.broadcast({"type": "emergency_sell_executed", "closed_trades": closed_trades})
    
    return {"status": "success", "closed_positions": len(closed_trades)}

@app.get("/api/trades")
async def get_active_trades():
    return {"trades": active_trades[:10]}  # Return last 10 trades

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Update prices every 5 seconds
            current_time = time.time()
            if current_time - last_update > 5:
                await fetch_crypto_prices()
            
            # Broadcast current data
            await manager.broadcast({
                "type": "price_update",
                "data": CRYPTO_PAIRS
            })
            
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)