from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
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
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# Binance API settings
BINANCE_API_URL = "https://api.binance.com/api/v3"
CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT", "DOTUSDT"]

# Global data store
CRYPTO_PAIRS = {}
last_binance_update = 0

async def fetch_binance_prices():
    """Fetch real prices from CoinGecko API (fallback)"""
    global CRYPTO_PAIRS, last_binance_update
    
    try:
        # CoinGecko API mapping
        coin_mapping = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum", 
            "BNBUSDT": "binancecoin",
            "ADAUSDT": "cardano",
            "SOLUSDT": "solana",
            "DOTUSDT": "polkadot"
        }
        
        # Get current prices
        coin_ids = ",".join(coin_mapping.values())
        price_response = requests.get(
            f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true", 
            timeout=10
        )
        
        if price_response.status_code == 200:
            price_data = price_response.json()
        else:
            print("Failed to fetch prices from CoinGecko")
            return False
        
        # Update our data
        for symbol, coin_id in coin_mapping.items():
            if coin_id in price_data:
                coin_data = price_data[coin_id]
                
                # Format symbol for display
                base = symbol.replace('USDT', '')
                display_symbol = f"{base}/USDT"
                
                current_price = coin_data['usd']
                price_change = coin_data.get('usd_24h_change', 0)
                volume = coin_data.get('usd_24h_vol', 0)
                
                # Calculate high/low from change
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
        
        last_binance_update = time.time()
        print(f"✅ Updated prices from CoinGecko API for {len(CRYPTO_PAIRS)} pairs")
        return True
        
    except Exception as e:
        print(f"❌ Error fetching CoinGecko data: {str(e)}")
        # Fallback to mock data if both APIs fail
        await initialize_mock_data()
        return True

async def initialize_mock_data():
    """Initialize with realistic mock data as fallback"""
    global CRYPTO_PAIRS
    
    CRYPTO_PAIRS = {
        "BTCUSDT": {"symbol": "BTC/USDT", "price": 43251.50, "change": 2.45, "volume": 125000000, "high24h": 44100.00, "low24h": 42800.00, "lastUpdate": datetime.now().isoformat()},
        "ETHUSDT": {"symbol": "ETH/USDT", "price": 2651.75, "change": -1.23, "volume": 89000000, "high24h": 2720.50, "low24h": 2580.25, "lastUpdate": datetime.now().isoformat()},
        "BNBUSDT": {"symbol": "BNB/USDT", "price": 315.20, "change": 0.85, "volume": 45000000, "high24h": 325.80, "low24h": 308.90, "lastUpdate": datetime.now().isoformat()},
        "ADAUSDT": {"symbol": "ADA/USDT", "price": 0.4856, "change": 3.21, "volume": 28000000, "high24h": 0.5120, "low24h": 0.4650, "lastUpdate": datetime.now().isoformat()},
        "SOLUSDT": {"symbol": "SOL/USDT", "price": 98.45, "change": -2.10, "volume": 67000000, "high24h": 105.20, "low24h": 95.80, "lastUpdate": datetime.now().isoformat()},
        "DOTUSDT": {"symbol": "DOT/USDT", "price": 7.85, "change": 1.45, "volume": 23000000, "high24h": 8.15, "low24h": 7.60, "lastUpdate": datetime.now().isoformat()}
    }
    print("✅ Initialized with mock data as fallback")

# Initialize with Binance data
asyncio.create_task(fetch_binance_prices())

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
    openai_api_key: str = ""
    ai_model: str = "gpt-4o"
    ai_provider: str = "openai"
    enable_ai_signals: bool = False
    price_update_interval: int = 5  # seconds (1-3600)

class TradeOrder(BaseModel):
    id: str
    pair: str
    side: str  # "BUY" or "SELL"
    amount: float
    price: float
    market_type: str  # "spot" or "futures"
    timestamp: datetime
    status: str = "filled"
    ai_signal: Optional[str] = None

class AISignal(BaseModel):
    pair: str
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float
    analysis: str
    timestamp: datetime

# Global settings
current_settings = TradeSettings()
active_trades = []
ai_signals = {}

async def get_ai_trading_signal(pair: str, price_data: dict) -> Optional[AISignal]:
    """Get trading signal from AI - Simplified version without AI integration"""
    if not current_settings.enable_ai_signals:
        return None
    
    # Simplified mock AI signal generation based on price change
    try:
        price_change = price_data.get('change', 0)
        
        # Simple logic based on price movement
        if price_change > 2:
            signal = "BUY"
            confidence = min(75 + abs(price_change) * 2, 95)
            analysis = f"Strong upward momentum with {price_change:.2f}% gain"
        elif price_change < -2:
            signal = "SELL"
            confidence = min(75 + abs(price_change) * 2, 95)
            analysis = f"Downward trend with {price_change:.2f}% decline"
        else:
            signal = "HOLD"
            confidence = 60
            analysis = f"Sideways movement with {price_change:.2f}% change"
        
        return AISignal(
            pair=pair,
            signal=signal,
            confidence=confidence,
            analysis=analysis,
            timestamp=datetime.now()
        )
    
    except Exception as e:
        print(f"AI Signal Error for {pair}: {str(e)}")
        return None

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/pairs")
async def get_crypto_pairs():
    """Get current pairs data"""
    if not CRYPTO_PAIRS:
        await fetch_binance_prices()
    return {"pairs": CRYPTO_PAIRS}

@app.get("/api/pairs/all")
async def get_all_pairs_with_signals():
    """Get all pairs with current AI signals"""
    if not CRYPTO_PAIRS:
        await fetch_binance_prices()
        
    pairs_with_signals = {}
    
    for pair_key, pair_data in CRYPTO_PAIRS.items():
        pairs_with_signals[pair_key] = {
            **pair_data,
            "ai_signal": ai_signals.get(pair_key, None)
        }
    
    return {"pairs": pairs_with_signals}

@app.post("/api/refresh-prices")
async def refresh_binance_prices():
    """Manually refresh prices from Binance"""
    success = await fetch_binance_prices()
    if success:
        await manager.broadcast({
            "type": "price_update",
            "data": CRYPTO_PAIRS,
            "ai_signals": ai_signals
        })
        return {"status": "success", "message": "Prices updated from Binance"}
    else:
        return JSONResponse(status_code=500, content={"error": "Failed to update prices"})

@app.get("/api/settings")
async def get_settings():
    # Don't expose the API key in responses
    settings_dict = current_settings.dict()
    if settings_dict.get("openai_api_key"):
        settings_dict["openai_api_key"] = "***HIDDEN***"
    return settings_dict

@app.post("/api/settings")
async def update_settings(settings: TradeSettings):
    global current_settings
    current_settings = settings
    return {"status": "updated", "settings": "Settings updated successfully"}

@app.post("/api/trade/{pair}")
async def execute_trade(pair: str, side: str, market_type: str = "spot"):
    if pair not in CRYPTO_PAIRS:
        return JSONResponse(status_code=404, content={"error": "Pair not found"})
    
    current_price = CRYPTO_PAIRS[pair]["price"]
    trade_id = str(uuid.uuid4())
    
    # Simulate slight slippage
    slippage = random.uniform(-0.001, 0.001)
    execution_price = current_price * (1 + slippage)
    
    # Get AI signal for this trade
    ai_signal_text = None
    if current_settings.enable_ai_signals and pair in ai_signals:
        signal_data = ai_signals[pair]
        ai_signal_text = f"{signal_data['signal']} ({signal_data['confidence']}%)"
    
    trade = TradeOrder(
        id=trade_id,
        pair=pair,
        side=side,
        amount=current_settings.trade_amount,
        price=execution_price,
        market_type=market_type,
        timestamp=datetime.now(),
        ai_signal=ai_signal_text
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

@app.get("/api/ai-signals")
async def get_ai_signals():
    """Get current AI trading signals for all pairs"""
    return {"signals": ai_signals}

@app.post("/api/generate-ai-signals")
async def generate_ai_signals():
    """Generate AI signals for all pairs"""
    if not current_settings.openai_api_key or not current_settings.enable_ai_signals:
        return JSONResponse(status_code=400, content={"error": "AI signals not configured"})
    
    generated_signals = {}
    
    for pair_key, pair_data in CRYPTO_PAIRS.items():
        signal = await get_ai_trading_signal(pair_key, pair_data)
        if signal:
            generated_signals[pair_key] = {
                "signal": signal.signal,
                "confidence": signal.confidence,
                "analysis": signal.analysis,
                "timestamp": signal.timestamp.isoformat()
            }
    
    # Update global signals
    ai_signals.update(generated_signals)
    
    # Broadcast new signals
    await manager.broadcast({
        "type": "ai_signals_updated",
        "signals": generated_signals
    })
    
    return {"status": "success", "signals": generated_signals}

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Check if we need to update from Binance
            current_time = time.time()
            if current_time - last_binance_update > current_settings.price_update_interval:
                await fetch_binance_prices()
            
            # Broadcast current data
            await manager.broadcast({
                "type": "price_update",
                "data": CRYPTO_PAIRS,
                "ai_signals": ai_signals,
                "update_interval": current_settings.price_update_interval
            })
            
            # Wait for the configured interval
            await asyncio.sleep(current_settings.price_update_interval)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)