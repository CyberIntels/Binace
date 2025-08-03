import React, { useState, useEffect, useCallback } from 'react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { AlertTriangle, TrendingUp, TrendingDown, Zap, Activity, Settings, DollarSign } from 'lucide-react';
import './App.css';

const App = () => {
  const [selectedPair, setSelectedPair] = useState('BTCUSDT');
  const [marketType, setMarketType] = useState('spot');
  const [pairs, setPairs] = useState({});
  const [settings, setSettings] = useState({
    trade_amount: 500,
    take_profit: 10,
    stop_loss: 3,
    timeframe: '5m',
    activation_distance: 1.5
  });
  const [trades, setTrades] = useState([]);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // WebSocket connection
  useEffect(() => {
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

  // Load initial data
  useEffect(() => {
    loadPairs();
    loadSettings();
    loadTrades();
  }, []);

  const loadPairs = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/pairs`);
      const data = await response.json();
      setPairs(data.pairs);
    } catch (error) {
      console.error('Failed to load pairs:', error);
    }
  };

  const loadSettings = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/settings`);
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Failed to load settings:', error);
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

  const updateSettings = async (newSettings) => {
    try {
      await fetch(`${BACKEND_URL}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings)
      });
      setSettings(newSettings);
    } catch (error) {
      console.error('Failed to update settings:', error);
    }
  };

  const executeTrade = async (side) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/trade/${selectedPair}?side=${side}&market_type=${marketType}`, {
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
  const volume = currentPair?.volume || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Activity className="w-8 h-8 text-yellow-400" />
                <h1 className="text-2xl font-bold text-white">Binance Trader</h1>
              </div>
              <Badge variant={connected ? "default" : "destructive"} className="text-xs">
                {connected ? `● LIVE ${lastUpdate}` : '● DISCONNECTED'}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="text-slate-300 border-slate-600">
                Balance: $12,450.50
              </Badge>
              <Button
                onClick={emergencySell}
                className="bg-red-600 hover:bg-red-700 text-white font-bold px-6"
              >
                <AlertTriangle className="w-4 h-4 mr-2" />
                EMERGENCY SELL
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Trading Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Pair Selection & Market Type */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <DollarSign className="w-5 h-5" />
                  <span>Trading Panel</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-slate-300">Trading Pair</Label>
                    <Select value={selectedPair} onValueChange={setSelectedPair}>
                      <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-700 border-slate-600">
                        {Object.entries(pairs).map(([key, pair]) => (
                          <SelectItem key={key} value={key} className="text-white hover:bg-slate-600">
                            {pair.symbol}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div>
                    <Label className="text-slate-300">Market Type</Label>
                    <div className="flex space-x-2 mt-2">
                      <Button
                        variant={marketType === 'spot' ? 'default' : 'outline'}
                        onClick={() => setMarketType('spot')}
                        className="flex-1"
                      >
                        ⚡ Spot
                      </Button>
                      <Button
                        variant={marketType === 'futures' ? 'default' : 'outline'}
                        onClick={() => setMarketType('futures')}
                        className="flex-1"
                      >
                        ♾️ Futures
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Price Display */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="py-6">
                <div className="text-center space-y-2">
                  <h2 className="text-3xl font-mono font-bold text-white">
                    ${currentPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 })}
                  </h2>
                  <div className="flex items-center justify-center space-x-4">
                    <Badge
                      variant={priceChange >= 0 ? "default" : "destructive"}
                      className={`${priceChange >= 0 ? 'bg-green-600' : 'bg-red-600'} text-white`}
                    >
                      {priceChange >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                      {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%
                    </Badge>
                    <span className="text-slate-400 text-sm">
                      Vol: ${volume.toLocaleString()}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Buy/Sell Buttons */}
            <div className="grid grid-cols-2 gap-4">
              <Button
                onClick={() => executeTrade('BUY')}
                className="h-20 text-xl font-bold bg-green-600 hover:bg-green-700 text-white transform transition-all duration-200 hover:scale-105 shadow-lg"
              >
                <TrendingUp className="w-6 h-6 mr-2" />
                BUY NOW
              </Button>
              <Button
                onClick={() => executeTrade('SELL')}
                className="h-20 text-xl font-bold bg-red-600 hover:bg-red-700 text-white transform transition-all duration-200 hover:scale-105 shadow-lg"
              >
                <TrendingDown className="w-6 h-6 mr-2" />
                SELL NOW
              </Button>
            </div>
          </div>

          {/* Settings & Info Panel */}
          <div className="space-y-6">
            {/* Settings */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center space-x-2">
                  <Settings className="w-5 h-5" />
                  <span>Trade Settings</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-slate-300">Trade Amount (USDT)</Label>
                  <Input
                    type="number"
                    value={settings.trade_amount}
                    onChange={(e) => updateSettings({...settings, trade_amount: parseFloat(e.target.value)})}
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-slate-300 text-sm">Take Profit (%)</Label>
                    <Input
                      type="number"
                      value={settings.take_profit}
                      onChange={(e) => updateSettings({...settings, take_profit: parseFloat(e.target.value)})}
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                  </div>
                  <div>
                    <Label className="text-slate-300 text-sm">Stop Loss (%)</Label>
                    <Input
                      type="number"
                      value={settings.stop_loss}
                      onChange={(e) => updateSettings({...settings, stop_loss: parseFloat(e.target.value)})}
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-slate-300">Timeframe</Label>
                  <Select value={settings.timeframe} onValueChange={(value) => updateSettings({...settings, timeframe: value})}>
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-700 border-slate-600">
                      <SelectItem value="1m" className="text-white">1 minute</SelectItem>
                      <SelectItem value="5m" className="text-white">5 minutes</SelectItem>
                      <SelectItem value="15m" className="text-white">15 minutes</SelectItem>
                      <SelectItem value="1h" className="text-white">1 hour</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Recent Trades */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Recent Trades</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {trades.slice(0, 5).map((trade, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-slate-700/50 rounded">
                      <div>
                        <span className="text-white text-sm font-medium">{trade.pair}</span>
                        <span className={`ml-2 text-xs ${trade.side === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                          {trade.side}
                        </span>
                      </div>
                      <div className="text-right">
                        <div className="text-white text-sm">${trade.price.toFixed(2)}</div>
                        <div className="text-slate-400 text-xs">${trade.amount}</div>
                      </div>
                    </div>
                  ))}
                  {trades.length === 0 && (
                    <div className="text-slate-400 text-center py-4">No trades yet</div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;