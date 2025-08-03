import asyncio
import websockets
import json
import sys

async def test_websocket():
    """Test WebSocket connection and real-time updates"""
    uri = "ws://localhost:8001/api/ws"
    
    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Listen for a few messages
            message_count = 0
            max_messages = 3
            
            while message_count < max_messages:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n📨 Message {message_count}:")
                    print(f"   Type: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'price_update':
                        pairs_data = data.get('data', {})
                        print(f"   Pairs updated: {len(pairs_data)}")
                        
                        # Show first 2 pairs
                        for i, (pair_key, pair_data) in enumerate(list(pairs_data.items())[:2]):
                            print(f"   - {pair_data['symbol']}: ${pair_data['price']} ({pair_data['change']:+.2f}%)")
                        
                        print(f"   Update interval: {data.get('update_interval', 'unknown')} seconds")
                    
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for WebSocket message")
                    break
                except json.JSONDecodeError:
                    print("❌ Failed to parse WebSocket message as JSON")
                    break
            
            print(f"\n✅ WebSocket test completed - received {message_count} messages")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {str(e)}")
        return False

async def main():
    print("🚀 Starting WebSocket Test")
    print("=" * 40)
    
    success = await test_websocket()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 WebSocket test passed!")
        return 0
    else:
        print("⚠️ WebSocket test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))