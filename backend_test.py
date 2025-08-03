import requests
import sys
import json
from datetime import datetime

class BinanceTradingAPITester:
    def __init__(self, base_url="https://7f2ff7e3-cef4-4159-8b7f-c2fcce433756.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health endpoint"""
        return self.run_test("Health Check", "GET", "api/health", 200)

    def test_get_pairs(self):
        """Test getting crypto pairs"""
        success, data = self.run_test("Get Crypto Pairs", "GET", "api/pairs", 200)
        if success and 'pairs' in data:
            pairs = data['pairs']
            print(f"   Found {len(pairs)} trading pairs")
            for pair_key, pair_data in list(pairs.items())[:3]:  # Show first 3
                print(f"   - {pair_data['symbol']}: ${pair_data['price']} ({pair_data['change']:+.2f}%)")
        return success, data

    def test_get_settings(self):
        """Test getting current settings"""
        return self.run_test("Get Settings", "GET", "api/settings", 200)

    def test_update_settings(self):
        """Test updating settings"""
        new_settings = {
            "trade_amount": 1000,
            "take_profit": 15,
            "stop_loss": 5,
            "timeframe": "1h",
            "activation_distance": 2.0
        }
        return self.run_test("Update Settings", "POST", "api/settings", 200, data=new_settings)

    def test_execute_buy_trade(self):
        """Test executing a BUY trade"""
        return self.run_test("Execute BUY Trade", "POST", "api/trade/BTCUSDT", 200, params={"side": "BUY", "market_type": "spot"})

    def test_execute_sell_trade(self):
        """Test executing a SELL trade"""
        return self.run_test("Execute SELL Trade", "POST", "api/trade/ETHUSDT", 200, params={"side": "SELL", "market_type": "futures"})

    def test_invalid_pair_trade(self):
        """Test trading with invalid pair"""
        return self.run_test("Invalid Pair Trade", "POST", "api/trade/INVALIDPAIR", 404, params={"side": "BUY"})

    def test_get_trades(self):
        """Test getting active trades"""
        return self.run_test("Get Active Trades", "GET", "api/trades", 200)

    def test_emergency_sell(self):
        """Test emergency sell functionality"""
        return self.run_test("Emergency Sell", "POST", "api/emergency-sell", 200)

    def test_get_all_pairs_with_signals(self):
        """Test getting all pairs with AI signals"""
        return self.run_test("Get All Pairs with Signals", "GET", "api/pairs/all", 200)

    def test_get_ai_signals(self):
        """Test getting AI signals"""
        return self.run_test("Get AI Signals", "GET", "api/ai-signals", 200)

    def test_generate_ai_signals_without_key(self):
        """Test generating AI signals without API key (should fail)"""
        return self.run_test("Generate AI Signals (No Key)", "POST", "api/generate-ai-signals", 400)

    def test_ai_settings_update(self):
        """Test updating AI-related settings"""
        ai_settings = {
            "trade_amount": 500,
            "take_profit": 10,
            "stop_loss": 3,
            "timeframe": "5m",
            "activation_distance": 1.5,
            "openai_api_key": "test-key-123",
            "ai_model": "gpt-4o",
            "ai_provider": "openai",
            "enable_ai_signals": True
        }
        return self.run_test("Update AI Settings", "POST", "api/settings", 200, data=ai_settings)

def main():
    print("🚀 Starting Binance Trading API Tests")
    print("=" * 50)
    
    tester = BinanceTradingAPITester()

    # Test sequence
    print("\n📋 Running API Tests...")
    
    # Basic health and data endpoints
    tester.test_health_check()
    tester.test_get_pairs()
    tester.test_get_settings()
    
    # Settings management
    tester.test_update_settings()
    tester.test_get_settings()  # Verify settings were updated
    
    # Trading functionality
    tester.test_execute_buy_trade()
    tester.test_execute_sell_trade()
    tester.test_invalid_pair_trade()  # Error handling
    
    # Trade management
    tester.test_get_trades()
    tester.test_emergency_sell()
    tester.test_get_trades()  # Verify trades were cleared
    
    # AI-related endpoints
    tester.test_get_all_pairs_with_signals()
    tester.test_get_ai_signals()
    tester.test_ai_settings_update()
    tester.test_generate_ai_signals_without_key()  # Should fail without proper API key
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend API tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())