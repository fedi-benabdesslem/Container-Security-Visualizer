#!/usr/bin/env python3
# test_websocket.py - Test WebSocket connection

import asyncio
import websockets
import json


async def test_websocket():
    uri = "ws://localhost:8000/ws/events"

    print(f"Connecting to {uri}...")

    async with websockets.connect(uri) as websocket:
        print("✅ Connected!")

        # Listen for events
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)

                if data.get("type") == "connected":
                    print(f"📡 {data.get('message')}")
                    print(f"   Active connections: {data.get('active_connections')}")
                else:
                    # Real event
                    print(f"\n🔔 New Event:")
                    print(f"   ID: {data.get('id')}")
                    print(f"   Type: {data.get('monitor_type')}")
                    print(f"   PID: {data.get('pid')}")
                    print(f"   Container: {data.get('container_name')}")
                    if data.get('risk_score'):
                        print(f"   Risk Score: {data.get('risk_score')}")

        except KeyboardInterrupt:
            print("\n👋 Disconnecting...")


if __name__ == "__main__":
    asyncio.run(test_websocket())
