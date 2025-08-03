import React, { useState, useEffect, useCallback } from 'react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Switch } from './components/ui/switch';
import { AlertTriangle, TrendingUp, TrendingDown, Zap, Activity, Settings, DollarSign, Bot, Brain, Eye, RotateCw, Clock } from 'lucide-react';
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
    activation_distance: 1.5,
    openai_api_key: '',
    ai_model: 'gpt-4o',
    ai_provider: 'openai',
    enable_ai_signals: false,
    price_update_interval: 5
  });
  const [trades, setTrades] = useState([]);
  const [aiSignals, setAiSignals] = useState({});
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [generatingSignals, setGeneratingSignals] = useState(false);
  const [refreshingPrices, setRefreshingPrices] = useState(false);

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
        if (data.ai_signals) {
          setAiSignals(data.ai_signals);
        }
        setLastUpdate(new Date().toLocaleTimeString());
      } else if (data.type === 'trade_executed') {
        setTrades(prev => [data.trade, ...prev]);
      } else if (data.type === 'ai_signals_updated') {
        setAiSignals(prev => ({ ...prev, ...data.signals }));
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
    loadAiSignals();
  }, []);

  const loadPairs = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/pairs/all`);
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

  const loadAiSignals = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/ai-signals`);
      const data = await response.json();
      setAiSignals(data.signals);
    } catch (error) {
      console.error('Failed to load AI signals:', error);
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

  const refreshPrices = async () => {
    setRefreshingPrices(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/refresh-prices`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.status === 'success') {
        console.log('Prices refreshed from Binance');
      }
    } catch (error) {
      console.error('Failed to refresh prices:', error);
    } finally {
      setRefreshingPrices(false);
    }
  };

  const generateAiSignals = async () => {
    if (!settings.openai_api_key) {
      alert('Please set your OpenAI API key in settings first');
      return;
    }
    
    setGeneratingSignals(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/generate-ai-signals`, {
        method: 'POST'
      });
      const result = await response.json();
      
      if (result.status === 'success') {
        setAiSignals(prev => ({ ...prev, ...result.signals }));
      } else {
        alert('Failed to generate AI signals: ' + result.error);
      }
    } catch (error) {
      console.error('Failed to generate AI signals:', error);
      alert('Error generating AI signals');
    } finally {
      setGeneratingSignals(false);
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
  const currentSignal = aiSignals[selectedPair];

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'BUY': return 'bg-emerald-600';
      case 'SELL': return 'bg-red-600';
      case 'HOLD': return 'bg-amber-600';
      default: return 'bg-neutral-600';
    }
  };

  const formatPrice = (price) => {
    if (!price) return '0.00';
    return price > 1 
      ? price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
      : price.toFixed(8);
  };

  const getUpdateIntervalText = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950">
      {/* Header */}
      <div className="border-b border-neutral-800 bg-neutral-900/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Activity className="w-6 h-6 text-emerald-400" />
                <h1 className="text-xl font-bold text-white">Binance Trader</h1>
                {settings.enable_ai_signals && (
                  <Badge variant="outline" className="text-emerald-400 border-emerald-400/30 bg-emerald-400/10">
                    <Bot className="w-3 h-3 mr-1" />
                    AI
                  </Badge>
                )}
              </div>
              <Badge variant={connected ? "default" : "destructive"} className={`text-xs ${connected ? 'bg-emerald-600' : 'bg-red-600'} animated-border`}>
                {connected ? `● LIVE ${lastUpdate}` : '● OFFLINE'}
              </Badge>
              <Badge variant="outline" className="text-xs text-neutral-400 border-neutral-700">
                <Clock className="w-3 h-3 mr-1" />
                {getUpdateIntervalText(settings.price_update_interval)}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <Badge variant="outline" className="text-neutral-300 border-neutral-700 text-sm px-3">
                Balance: $12,450.50
              </Badge>
              <Button
                onClick={refreshPrices}
                disabled={refreshingPrices}
                size="sm"
                className="bg-neutral-700 hover:bg-neutral-600 text-white px-3"
              >
                <RotateCw className={`w-4 h-4 ${refreshingPrices ? 'animate-spin' : ''}`} />
              </Button>
              {settings.enable_ai_signals && (
                <Button
                  onClick={generateAiSignals}
                  disabled={generatingSignals}
                  size="sm"
                  className="bg-emerald-600 hover:bg-emerald-700 text-white px-3"
                >
                  <Brain className="w-4 h-4 mr-1" />
                  {generatingSignals ? 'AI...' : 'AI'}
                </Button>
              )}
              <Button
                onClick={emergencySell}
                size="sm"
                className="bg-red-600 hover:bg-red-700 text-white font-bold px-4 animated-border-red"
              >
                <AlertTriangle className="w-4 h-4 mr-1" />
                EMERGENCY
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Market Overview */}
          <div className="lg:col-span-1">
            <Card className="bg-neutral-900/50 border-neutral-800 h-fit">
              <CardHeader className="pb-3">
                <CardTitle className="text-white flex items-center space-x-2 text-sm">
                  <Eye className="w-4 h-4" />
                  <span>Markets</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {Object.entries(pairs).map(([key, pair]) => {
                    const signal = aiSignals[key];
                    const isSelected = key === selectedPair;
                    
                    return (
                      <div 
                        key={key}
                        onClick={() => setSelectedPair(key)}
                        className={`p-2 rounded-lg cursor-pointer transition-all duration-200 ${
                          isSelected 
                            ? 'bg-neutral-800/80 border border-emerald-500/30 animated-border' 
                            : 'bg-neutral-800/30 hover:bg-neutral-700/50'
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <div className="text-white font-medium text-sm">{pair.symbol}</div>
                            <div className="text-neutral-400 text-xs">
                              ${formatPrice(pair.price)}
                            </div>
                          </div>
                          <div className="text-right">
                            <Badge
                              variant={pair.change >= 0 ? "default" : "destructive"}
                              className={`text-xs ${pair.change >= 0 ? 'bg-emerald-600' : 'bg-red-600'} text-white`}
                            >
                              {pair.change >= 0 ? '+' : ''}{pair.change?.toFixed(2)}%
                            </Badge>
                            {signal && (
                              <div className="mt-1">
                                <Badge 
                                  className={`text-xs ${getSignalColor(signal.signal)} text-white`}
                                >
                                  {signal.signal}
                                </Badge>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Trading Panel */}
          <div className="lg:col-span-2 space-y-4">
            {/* Price Display */}
            <Card className="bg-neutral-900/50 border-neutral-800 animated-border">
              <CardContent className="py-6">
                <div className="text-center space-y-4">
                  <div>
                    <h2 className="text-3xl font-mono font-bold text-white">
                      ${formatPrice(currentPrice)}
                    </h2>
                    <div className="text-neutral-400 text-sm">{pairs[selectedPair]?.symbol}</div>
                  </div>
                  
                  <div className="flex items-center justify-center space-x-4">
                    <Badge
                      variant={priceChange >= 0 ? "default" : "destructive"}
                      className={`px-3 py-1 ${priceChange >= 0 ? 'bg-emerald-600' : 'bg-red-600'} text-white`}
                    >
                      {priceChange >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                      {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}%
                    </Badge>
                    
                    {currentSignal && (
                      <Badge className={`px-3 py-1 ${getSignalColor(currentSignal.signal)} text-white`}>
                        <Bot className="w-3 h-3 mr-1" />
                        {currentSignal.signal} {currentSignal.confidence}%
                      </Badge>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-center text-sm">
                    <div>
                      <div className="text-neutral-500">24h High</div>
                      <div className="text-white font-mono">${formatPrice(currentPair?.high24h)}</div>
                    </div>
                    <div>
                      <div className="text-neutral-500">Volume</div>
                      <div className="text-white font-mono">${volume.toLocaleString(undefined, {maximumFractionDigits: 0})}</div>
                    </div>
                    <div>
                      <div className="text-neutral-500">24h Low</div>
                      <div className="text-white font-mono">${formatPrice(currentPair?.low24h)}</div>
                    </div>
                  </div>

                  {currentSignal && (
                    <div className="mt-3 p-3 bg-neutral-800/50 rounded-lg text-left">
                      <div className="text-xs text-neutral-400">AI Analysis:</div>
                      <div className="text-white text-sm mt-1">{currentSignal.analysis}</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Trading Controls */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-neutral-300 text-sm">Market Type</Label>
                <div className="flex space-x-2">
                  <Button
                    variant={marketType === 'spot' ? 'default' : 'outline'}
                    onClick={() => setMarketType('spot')}
                    size="sm"
                    className="flex-1 bg-neutral-700 hover:bg-neutral-600"
                  >
                    ⚡ Spot
                  </Button>
                  <Button
                    variant={marketType === 'futures' ? 'default' : 'outline'}
                    onClick={() => setMarketType('futures')}
                    size="sm"
                    className="flex-1 bg-neutral-700 hover:bg-neutral-600"
                  >
                    ♾️ Futures
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-neutral-300 text-sm">Amount (USDT)</Label>
                <Input
                  type="number"
                  value={settings.trade_amount}
                  onChange={(e) => updateSettings({...settings, trade_amount: parseFloat(e.target.value)})}
                  className="bg-neutral-800 border-neutral-700 text-white text-sm"
                />
              </div>
            </div>

            {/* Trading Buttons */}
            <div className="grid grid-cols-2 gap-3">
              <Button
                onClick={() => executeTrade('BUY')}
                className="h-12 text-base font-bold bg-emerald-600 hover:bg-emerald-700 text-white animated-border-green"
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                BUY
              </Button>
              <Button
                onClick={() => executeTrade('SELL')}
                className="h-12 text-base font-bold bg-red-600 hover:bg-red-700 text-white animated-border-red"
              >
                <TrendingDown className="w-4 h-4 mr-2" />
                SELL
              </Button>
            </div>
          </div>

          {/* Settings Panel */}
          <div className="lg:col-span-1 space-y-4">
            <Card className="bg-neutral-900/50 border-neutral-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-white flex items-center space-x-2 text-sm">
                  <Settings className="w-4 h-4" />
                  <span>Settings</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Tabs defaultValue="trading" className="w-full">
                  <TabsList className="grid w-full grid-cols-2 bg-neutral-800">
                    <TabsTrigger value="trading" className="text-white text-xs">Trading</TabsTrigger>
                    <TabsTrigger value="ai" className="text-white text-xs">AI</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="trading" className="space-y-3 mt-4">
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Label className="text-neutral-300 text-xs">Take Profit (%)</Label>
                        <Input
                          type="number"
                          value={settings.take_profit}
                          onChange={(e) => updateSettings({...settings, take_profit: parseFloat(e.target.value)})}
                          className="bg-neutral-800 border-neutral-700 text-white text-sm"
                        />
                      </div>
                      <div>
                        <Label className="text-neutral-300 text-xs">Stop Loss (%)</Label>
                        <Input
                          type="number"
                          value={settings.stop_loss}
                          onChange={(e) => updateSettings({...settings, stop_loss: parseFloat(e.target.value)})}
                          className="bg-neutral-800 border-neutral-700 text-white text-sm"
                        />
                      </div>
                    </div>

                    <div>
                      <Label className="text-neutral-300 text-xs">Update Interval</Label>
                      <Select 
                        value={settings.price_update_interval.toString()} 
                        onValueChange={(value) => updateSettings({...settings, price_update_interval: parseInt(value)})}
                      >
                        <SelectTrigger className="bg-neutral-800 border-neutral-700 text-white text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-neutral-800 border-neutral-700">
                          <SelectItem value="1" className="text-white">1 second</SelectItem>
                          <SelectItem value="5" className="text-white">5 seconds</SelectItem>
                          <SelectItem value="10" className="text-white">10 seconds</SelectItem>
                          <SelectItem value="30" className="text-white">30 seconds</SelectItem>
                          <SelectItem value="60" className="text-white">1 minute</SelectItem>
                          <SelectItem value="300" className="text-white">5 minutes</SelectItem>
                          <SelectItem value="900" className="text-white">15 minutes</SelectItem>
                          <SelectItem value="3600" className="text-white">1 hour</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="ai" className="space-y-3 mt-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={settings.enable_ai_signals}
                        onCheckedChange={(checked) => updateSettings({...settings, enable_ai_signals: checked})}
                      />
                      <Label className="text-neutral-300 text-xs">Enable AI</Label>
                    </div>
                    
                    <div>
                      <Label className="text-neutral-300 text-xs">API Key</Label>
                      <Input
                        type="password"
                        placeholder="sk-..."
                        value={settings.openai_api_key === '***HIDDEN***' ? '' : settings.openai_api_key}
                        onChange={(e) => updateSettings({...settings, openai_api_key: e.target.value})}
                        className="bg-neutral-800 border-neutral-700 text-white text-sm"
                      />
                    </div>
                    
                    <div>
                      <Label className="text-neutral-300 text-xs">Model</Label>
                      <Select value={settings.ai_model} onValueChange={(value) => updateSettings({...settings, ai_model: value})}>
                        <SelectTrigger className="bg-neutral-800 border-neutral-700 text-white text-sm">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-neutral-800 border-neutral-700">
                          <SelectItem value="gpt-4o" className="text-white">GPT-4o</SelectItem>
                          <SelectItem value="gpt-4.1" className="text-white">GPT-4.1</SelectItem>
                          <SelectItem value="claude-sonnet-4-20250514" className="text-white">Claude</SelectItem>
                          <SelectItem value="gemini-2.0-flash" className="text-white">Gemini</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            {/* Recent Trades */}
            <Card className="bg-neutral-900/50 border-neutral-800">
              <CardHeader className="pb-3">
                <CardTitle className="text-white text-sm">Recent Trades</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {trades.slice(0, 3).map((trade, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-neutral-800/30 rounded text-sm">
                      <div>
                        <span className="text-white font-medium">{trade.pair}</span>
                        <span className={`ml-2 text-xs ${trade.side === 'BUY' ? 'text-emerald-400' : 'text-red-400'}`}>
                          {trade.side}
                        </span>
                        {trade.ai_signal && (
                          <div className="text-xs text-emerald-400 mt-1">
                            AI: {trade.ai_signal}
                          </div>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-white text-sm">${trade.price.toFixed(2)}</div>
                        <div className="text-neutral-400 text-xs">${trade.amount}</div>
                      </div>
                    </div>
                  ))}
                  {trades.length === 0 && (
                    <div className="text-neutral-400 text-center py-4 text-sm">No trades yet</div>
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