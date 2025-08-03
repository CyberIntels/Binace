from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import asyncio
import json
import random
import time
from datetime import datetime, timedelta
import uuid
from typing import Optional, List
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.binance_trader

# Mock crypto pairs with realistic prices
CRYPTO_PAIRS = {
    "BTCUSDT": {"symbol": "BTC/USDT", "price": 43250.50, "change": 2.45, "volume": 125000000},
    "ETHUSDT": {"symbol": "ETH/USDT", "price": 2650.75, "change": -1.23, "volume": 89000000},
    "BNBUSDT": {"symbol": "BNB/USDT", "price": 315.20, "change": 0.85, "volume": 45000000},
    "ADAUSDT": {"symbol": "ADA/USDT", "price": 0.4856, "change": 3.21, "volume": 28000000},
    "SOLUSDT": {"symbol": "SOL/USDT", "price": 98.45, "change": -2.10, "volume": 67000000},
    "DOTUSDT": {"symbol": "DOT/USDT", "price": 7.85, "change": 1.45, "volume": 23000000}
}

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

# Pydantic models
class TradeSettings(BaseModel):
    trade_amount: float = 500
    take_profit: float = 10
    stop_loss: float = 3
    timeframe: str = "5m"
    activation_distance: float = 1.5

class TradeOrder(BaseModel):
    id: str
    pair: str
    side: str  # "BUY" or "SELL"
    amount: float
    price: float
    market_type: str  # "spot" or "futures"
    timestamp: datetime
    status: str = "filled"

# Global settings
current_settings = TradeSettings()
active_trades = []

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/pairs")
async def get_crypto_pairs():
    return {"pairs": CRYPTO_PAIRS}

@app.get("/api/settings")
async def get_settings():
    return current_settings.dict()

@app.post("/api/settings")
async def update_settings(settings: TradeSettings):
    global current_settings
    current_settings = settings
    return {"status": "updated", "settings": settings.dict()}

@app.post("/api/trade/{pair}")
async def execute_trade(pair: str, side: str, market_type: str = "spot"):
    if pair not in CRYPTO_PAIRS:
        return JSONResponse(status_code=404, content={"error": "Pair not found"})
    
    current_price = CRYPTO_PAIRS[pair]["price"]
    trade_id = str(uuid.uuid4())
    
    # Simulate slight slippage
    slippage = random.uniform(-0.001, 0.001)
    execution_price = current_price * (1 + slippage)
    
    trade = TradeOrder(
        id=trade_id,
        pair=pair,
        side=side,
        amount=current_settings.trade_amount,
        price=execution_price,
        market_type=market_type,
        timestamp=datetime.now()
    )
    
    active_trades.append(trade.dict())
    
    # Broadcast trade execution
    await manager.broadcast({
        "type": "trade_executed",
        "trade": trade.dict()
    })
    
    return {"status": "success", "trade": trade.dict()}

@app.post("/api/emergency-sell")
async def emergency_sell():
    """Close all positions immediately"""
    global active_trades
    closed_trades = []
    
    for trade in active_trades:
        if trade["side"] == "BUY":  # Only close buy positions
            close_trade = {
                "id": str(uuid.uuid4()),
                "original_trade_id": trade["id"],
                "pair": trade["pair"],
                "side": "SELL",
                "amount": trade["amount"],
                "price": CRYPTO_PAIRS[trade["pair"]]["price"],
                "market_type": trade["market_type"],
                "timestamp": datetime.now(),
                "status": "emergency_close"
            }
            closed_trades.append(close_trade)
    
    active_trades = []  # Clear all positions
    
    await manager.broadcast({
        "type": "emergency_sell_executed",
        "closed_trades": closed_trades
    })
    
    return {"status": "success", "closed_positions": len(closed_trades)}

@app.get("/api/trades")
async def get_active_trades():
    return {"trades": active_trades}

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send real-time price updates
            for pair_key, pair_data in CRYPTO_PAIRS.items():
                # Simulate price movement
                change_percent = random.uniform(-0.5, 0.5)
                new_price = pair_data["price"] * (1 + change_percent / 100)
                CRYPTO_PAIRS[pair_key]["price"] = round(new_price, 8)
                CRYPTO_PAIRS[pair_key]["change"] = round(change_percent, 2)
            
            await manager.broadcast({
                "type": "price_update",
                "data": CRYPTO_PAIRS
            })
            
            await asyncio.sleep(1)  # Update every second
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)