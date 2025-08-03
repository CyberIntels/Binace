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
    """Fetch real prices from Binance API"""
    global CRYPTO_PAIRS, last_binance_update
    
    try:
        # Get current prices for all symbols
        price_response = requests.get(f"{BINANCE_API_URL}/ticker/price", timeout=5)
        if price_response.status_code == 200:
            prices = {item['symbol']: float(item['price']) for item in price_response.json()}
        else:
            print("Failed to fetch prices from Binance")
            return False
        
        # Get 24hr ticker statistics
        ticker_response = requests.get(f"{BINANCE_API_URL}/ticker/24hr", timeout=5)
        if ticker_response.status_code == 200:
            tickers = {item['symbol']: item for item in ticker_response.json()}
        else:
            print("Failed to fetch 24hr stats from Binance")
            return False
        
        # Update our data
        for symbol in CRYPTO_SYMBOLS:
            if symbol in prices and symbol in tickers:
                ticker = tickers[symbol]
                
                # Format symbol for display
                base = symbol.replace('USDT', '')
                display_symbol = f"{base}/USDT"
                
                CRYPTO_PAIRS[symbol] = {
                    "symbol": display_symbol,
                    "price": prices[symbol],
                    "change": float(ticker['priceChangePercent']),
                    "volume": float(ticker['quoteVolume']),
                    "high24h": float(ticker['highPrice']),
                    "low24h": float(ticker['lowPrice']),
                    "lastUpdate": datetime.now().isoformat()
                }
        
        last_binance_update = time.time()
        print(f"✅ Updated prices from Binance API for {len(CRYPTO_PAIRS)} pairs")
        return True
        
    except Exception as e:
        print(f"❌ Error fetching Binance data: {str(e)}")
        return False

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
    """Get trading signal from AI"""
    if not current_settings.openai_api_key or not current_settings.enable_ai_signals:
        return None
    
    try:
        # Create AI chat instance
        chat = LlmChat(
            api_key=current_settings.openai_api_key,
            session_id=f"trading-{pair}-{int(time.time())}",
            system_message="You are a professional crypto trading analyst. Provide concise trading signals based on market data."
        ).with_model(current_settings.ai_provider, current_settings.ai_model)
        
        # Prepare market analysis prompt
        analysis_prompt = f"""
        Analyze the current market data for {pair}:
        
        Current Price: ${price_data['price']}
        24h Change: {price_data['change']}%
        24h High: ${price_data['high24h']}
        24h Low: ${price_data['low24h']}
        Volume: ${price_data['volume']:,}
        
        Based on this data, provide:
        1. Trading signal: BUY, SELL, or HOLD
        2. Confidence level (1-100)
        3. Brief reason (max 50 words)
        
        Format your response as JSON:
        {{"signal": "BUY/SELL/HOLD", "confidence": 85, "analysis": "Brief analysis reason"}}
        """
        
        user_message = UserMessage(text=analysis_prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        try:
            ai_data = json.loads(response.strip())
            return AISignal(
                pair=pair,
                signal=ai_data.get("signal", "HOLD"),
                confidence=float(ai_data.get("confidence", 50)),
                analysis=ai_data.get("analysis", "No analysis available"),
                timestamp=datetime.now()
            )
        except json.JSONDecodeError:
            # Fallback parsing if AI doesn't return proper JSON
            if "BUY" in response.upper():
                signal = "BUY"
            elif "SELL" in response.upper():
                signal = "SELL"
            else:
                signal = "HOLD"
                
            return AISignal(
                pair=pair,
                signal=signal,
                confidence=50.0,
                analysis=response[:100],
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