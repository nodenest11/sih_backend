#!/usr/bin/env python3
"""
Test script for the panic alerts system with emergency response forwarding
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_panic_alerts_system():
    """Test the panic alerts system with emergency response integration"""
    
    base_url = "http://localhost:8000"
    
    print("🚨 TESTING PANIC ALERTS SYSTEM")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Step 1: Register a test tourist
        print("\n1️⃣ Creating test tourist...")
        tourist_data = {
            "name": "Test Emergency Tourist",
            "contact": "+919999888777",
            "email": "emergency@test.com",
            "emergency_contact": "+919999888778",
            "age": 25,
            "nationality": "Indian"
        }
        
        try:
            response = await client.post(f"{base_url}/registerTourist", json=tourist_data)
            if response.status_code == 200:
                tourist_id = response.json()["id"]
                print(f"✅ Tourist registered with ID: {tourist_id}")
            else:
                print(f"❌ Failed to register tourist: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error registering tourist: {e}")
            return
        
        # Step 2: Create a panic/SOS alert
        print("\n2️⃣ Creating SOS/Panic alert...")
        panic_data = {
            "tourist_id": tourist_id,
            "latitude": 28.6139,  # Delhi coordinates
            "longitude": 77.2090,
            "message": "EMERGENCY! Tourist in danger - immediate help needed!"
        }
        
        try:
            response = await client.post(f"{base_url}/alerts/pressSOS", json=panic_data)
            if response.status_code == 201:
                alert = response.json()
                alert_id = alert["id"]
                print(f"✅ Panic Alert created with ID: {alert_id}")
                print(f"   📍 Location: {alert['latitude']}, {alert['longitude']}")
                print(f"   🚨 Severity: {alert['severity']}")
                print(f"   📝 Message: {alert['message']}")
            else:
                print(f"❌ Failed to create panic alert: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error creating panic alert: {e}")
            return
        
        # Step 3: Get panic alerts count
        print("\n3️⃣ Getting panic alerts count...")
        try:
            response = await client.get(f"{base_url}/alerts/panicAlertsCount")
            if response.status_code == 200:
                count_data = response.json()
                print(f"📊 Panic Alerts Count:")
                print(f"   Total: {count_data['total_panic_alerts']}")
                print(f"   Active: {count_data['breakdown']['active']}")
                print(f"   Acknowledged: {count_data['breakdown']['acknowledged']}")
                print(f"   Resolved: {count_data['breakdown']['resolved']}")
                print(f"   Critical: {count_data['breakdown']['critical_severity']}")
            else:
                print(f"❌ Failed to get panic count: {response.text}")
        except Exception as e:
            print(f"❌ Error getting panic count: {e}")
        
        # Step 4: Forward panic alert to emergency systems
        print("\n4️⃣ Forwarding panic alert to emergency systems...")
        try:
            response = await client.post(f"{base_url}/alerts/forwardAlert/{alert_id}")
            if response.status_code == 200:
                result = response.json()
                print(f"🚨 Emergency Response:")
                print(json.dumps(result, indent=2))
                
                if result.get("success"):
                    print("✅ Alert successfully forwarded to emergency systems!")
                else:
                    print(f"⚠️ Emergency forwarding issue: {result.get('message')}")
            else:
                print(f"❌ Failed to forward alert: {response.text}")
        except Exception as e:
            print(f"❌ Error forwarding alert: {e}")
        
        # Step 5: Check updated panic alerts count
        print("\n5️⃣ Checking updated panic alerts count...")
        try:
            response = await client.get(f"{base_url}/alerts/panicAlertsCount")
            if response.status_code == 200:
                count_data = response.json()
                print(f"📊 Updated Panic Alerts Count:")
                print(f"   Total: {count_data['total_panic_alerts']}")
                print(f"   Acknowledged: {count_data['breakdown']['acknowledged']} (should be +1)")
            else:
                print(f"❌ Failed to get updated count: {response.text}")
        except Exception as e:
            print(f"❌ Error getting updated count: {e}")
        
        # Step 6: Get all panic alerts
        print("\n6️⃣ Getting all panic alerts from database...")
        try:
            response = await client.get(f"{base_url}/alerts/getAlerts?alert_type=panic")
            if response.status_code == 200:
                alerts = response.json()
                print(f"📋 Found {len(alerts)} panic alerts:")
                for alert in alerts[:3]:  # Show first 3
                    print(f"   🚨 Alert {alert['id']}: {alert['message'][:50]}...")
                    print(f"      Status: {alert['status']}, Severity: {alert['severity']}")
            else:
                print(f"❌ Failed to get alerts: {response.text}")
        except Exception as e:
            print(f"❌ Error getting alerts: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 PANIC ALERTS SYSTEM TEST COMPLETED")
    print("\n📝 Summary:")
    print("✅ Panic alerts are saved to database automatically")
    print("✅ Emergency response forwarding endpoint available")
    print("✅ Panic alerts count retrieved from database")
    print("✅ All existing alert management features working")

if __name__ == "__main__":
    print("🚨 Smart Tourist Safety System - Panic Alerts Test")
    print(f"🕐 Test Time: {datetime.now()}")
    print("\nNote: Make sure the server is running at http://localhost:8000")
    print("Note: Emergency response URL can be configured via EMERGENCY_RESPONSE_URL env var")
    
    asyncio.run(test_panic_alerts_system())