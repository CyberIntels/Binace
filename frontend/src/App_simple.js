import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [selectedPair, setSelectedPair] = useState('BTCUSDT');
  const [pairs, setPairs] = useState({});
  const [trades, setTrades] = useState([]);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [tradeAmount, setTradeAmount] = useState(500);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Load data from backend
  useEffect(() => {
    loadPairs();
    loadTrades();
    
    // WebSocket connection
    const ws = new WebSocket(`${BACKEND_URL.replace('http', 'ws')}/api/ws`);
    
    ws.onopen = () => {
      setConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'price_update') {
        setPairs(data.data);
        setLastUpdate(new Date().toLocaleTimeString());
      } else if (data.type === 'trade_executed') {
        setTrades(prev => [data.trade, ...prev]);
      }
    };
    
    ws.onclose = () => {
      setConnected(false);
      console.log('WebSocket disconnected');
    };
    
    return () => ws.close();
  }, [BACKEND_URL]);

  const loadPairs = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/pairs`);
      const data = await response.json();
      setPairs(data.pairs);
    } catch (error) {
      console.error('Failed to load pairs:', error);
    }
  };

  const loadTrades = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/trades`);
      const data = await response.json();
      setTrades(data.trades);
    } catch (error) {
      console.error('Failed to load trades:', error);
    }
  };

  const executeTrade = async (side) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/trade/${selectedPair}?side=${side}&market_type=spot`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.status === 'success') {
        console.log(`${side} order executed:`, result.trade);
      }
    } catch (error) {
      console.error('Trade execution failed:', error);
    }
  };

  const emergencySell = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/emergency-sell`, {
        method: 'POST'
      });
      const result = await response.json();
      console.log('Emergency sell executed:', result);
      loadTrades();
    } catch (error) {
      console.error('Emergency sell failed:', error);
    }
  };

  const currentPair = pairs[selectedPair];
  const currentPrice = currentPair?.price || 0;
  const priceChange = currentPair?.change || 0;

  const formatPrice = (price) => {
    if (!price) return '0.00';
    return price > 1 
      ? price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
      : price.toFixed(8);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#1a1a1a', color: 'white', fontFamily: 'Arial, sans-serif' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#2d2d2d', padding: '15px', borderBottom: '1px solid #444' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ margin: 0, color: '#00d4aa' }}>⚡ Binance Trader</h1>
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <span style={{ 
              backgroundColor: connected ? '#00d4aa' : '#ff4444', 
              padding: '5px 10px', 
              borderRadius: '15px',
              fontSize: '12px'
            }}>
              {connected ? `● LIVE ${lastUpdate}` : '● OFFLINE'}
            </span>
            <button 
              onClick={emergencySell}
              style={{
                backgroundColor: '#ff4444',
                color: 'white',
                border: 'none',
                padding: '8px 15px',
                borderRadius: '5px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              🚨 EMERGENCY SELL
            </button>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', padding: '20px', gap: '20px' }}>
        
        {/* Left Panel - Market List */}
        <div style={{ flex: '1', backgroundColor: '#2d2d2d', borderRadius: '10px', padding: '15px' }}>
          <h3 style={{ margin: '0 0 15px 0' }}>📊 Markets</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.entries(pairs).map(([key, pair]) => (
              <div 
                key={key}
                onClick={() => setSelectedPair(key)}
                style={{
                  padding: '10px',
                  backgroundColor: key === selectedPair ? '#00d4aa' : '#3d3d3d',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  display: 'flex',
                  justifyContent: 'space-between'
                }}
              >
                <div>
                  <div style={{ fontWeight: 'bold' }}>{pair.symbol}</div>
                  <div style={{ fontSize: '12px', color: '#ccc' }}>
                    ${formatPrice(pair.price)}
                  </div>
                </div>
                <div style={{ 
                  color: pair.change >= 0 ? '#00d4aa' : '#ff4444',
                  fontWeight: 'bold'
                }}>
                  {pair.change >= 0 ? '+' : ''}{pair.change?.toFixed(2)}%
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Center Panel - Trading */}
        <div style={{ flex: '2', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Price Display */}
          <div style={{ backgroundColor: '#2d2d2d', borderRadius: '10px', padding: '30px', textAlign: 'center' }}>
            <h2 style={{ fontSize: '48px', margin: '0 0 10px 0', fontFamily: 'monospace' }}>
              ${formatPrice(currentPrice)}
            </h2>
            <div style={{ fontSize: '18px', color: '#ccc', marginBottom: '15px' }}>
              {pairs[selectedPair]?.symbol}
            </div>
            <div style={{ 
              fontSize: '20px', 
              color: priceChange >= 0 ? '#00d4aa' : '#ff4444',
              fontWeight: 'bold'
            }}>
              {priceChange >= 0 ? '📈 +' : '📉 '}{priceChange.toFixed(2)}%
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '20px', fontSize: '14px' }}>
              <div>
                <div style={{ color: '#ccc' }}>24h High</div>
                <div>${formatPrice(currentPair?.high24h)}</div>
              </div>
              <div>
                <div style={{ color: '#ccc' }}>Volume</div>
                <div>${currentPair?.volume?.toLocaleString(undefined, {maximumFractionDigits: 0}) || 0}</div>
              </div>
              <div>
                <div style={{ color: '#ccc' }}>24h Low</div>
                <div>${formatPrice(currentPair?.low24h)}</div>
              </div>
            </div>
          </div>

          {/* Trading Controls */}
          <div style={{ backgroundColor: '#2d2d2d', borderRadius: '10px', padding: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px' }}>Amount (USDT):</label>
              <input
                type="number"
                value={tradeAmount}
                onChange={(e) => setTradeAmount(parseFloat(e.target.value))}
                style={{
                  width: '100%',
                  padding: '10px',
                  backgroundColor: '#3d3d3d',
                  border: '1px solid #555',
                  borderRadius: '5px',
                  color: 'white'
                }}
              />
            </div>
            
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => executeTrade('BUY')}
                style={{
                  flex: 1,
                  padding: '15px',
                  backgroundColor: '#00d4aa',
                  border: 'none',
                  borderRadius: '5px',
                  color: 'white',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                📈 BUY
              </button>
              <button
                onClick={() => executeTrade('SELL')}
                style={{
                  flex: 1,
                  padding: '15px',
                  backgroundColor: '#ff4444',
                  border: 'none',
                  borderRadius: '5px',
                  color: 'white',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                📉 SELL
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel - Trades */}
        <div style={{ flex: '1', backgroundColor: '#2d2d2d', borderRadius: '10px', padding: '15px' }}>
          <h3 style={{ margin: '0 0 15px 0' }}>📝 Recent Trades</h3>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {trades.slice(0, 5).map((trade, index) => (
              <div 
                key={index} 
                style={{
                  padding: '10px',
                  backgroundColor: '#3d3d3d',
                  borderRadius: '5px',
                  marginBottom: '10px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 'bold' }}>{trade.pair}</div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: trade.side === 'BUY' ? '#00d4aa' : '#ff4444' 
                    }}>
                      {trade.side}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div>${trade.price?.toFixed(2)}</div>
                    <div style={{ fontSize: '12px', color: '#ccc' }}>${trade.amount}</div>
                  </div>
                </div>
              </div>
            ))}
            {trades.length === 0 && (
              <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                No trades yet
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;