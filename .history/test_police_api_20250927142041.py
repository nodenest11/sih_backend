#!/usr/bin/env python3
"""
Test script for the new police dashboard API endpoint
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_police_dashboard_api():
    """Test the new police dashboard API endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("🚔 TESTING POLICE DASHBOARD API INTEGRATION")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Step 1: Create a test tourist
        print("\n1️⃣ Creating test tourist...")
        tourist_data = {
            "name": "Emergency Test Tourist",
            "contact": "+919876543210",
            "email": "emergency.test@example.com",
            "emergency_contact": "+919876543211",
            "age": 30,
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
        
        # Step 2: Create an SOS/Panic alert
        print("\n2️⃣ Creating SOS/Panic alert...")
        sos_data = {
            "tourist_id": tourist_id,
            "latitude": 28.6139,  # New Delhi coordinates
            "longitude": 77.2090,
            "message": "Emergency SOS - Tourist in distress!"
        }
        
        try:
            response = await client.post(f"{base_url}/alerts/pressSOS", json=sos_data)
            if response.status_code == 201:
                alert = response.json()
                alert_id = alert["id"]
                print(f"✅ SOS Alert created with ID: {alert_id}")
                print(f"   📍 Location: {alert['latitude']}, {alert['longitude']}")
                print(f"   🚨 Severity: {alert['severity']}")
                print(f"   📝 Message: {alert['message']}")
            else:
                print(f"❌ Failed to create SOS alert: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error creating SOS alert: {e}")
            return
        
        # Step 3: Test sending alert to police dashboard
        print("\n3️⃣ Sending alert to police dashboard...")
        try:
            response = await client.post(f"{base_url}/alerts/sendToPoliceDashboard?alert_id={alert_id}")
            result = response.json()
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"🔄 API Response:")
            print(json.dumps(result, indent=2))
            
            if result.get("success"):
                print("✅ Alert successfully sent to police dashboard!")
            else:
                print(f"⚠️ Alert sending failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error sending to police dashboard: {e}")
        
        # Step 4: Check alert status
        print("\n4️⃣ Checking alert status...")
        try:
            response = await client.get(f"{base_url}/alerts/{alert_id}")
            if response.status_code == 200:
                alert_info = response.json()
                print(f"📋 Alert Status: {alert_info.get('status')}")
                print(f"👮 Acknowledged: {alert_info.get('acknowledged')}")
                print(f"🕐 Acknowledged At: {alert_info.get('acknowledged_at')}")
                print(f"👤 Acknowledged By: {alert_info.get('acknowledged_by')}")
            else:
                print(f"❌ Failed to get alert info: {response.text}")
        except Exception as e:
            print(f"❌ Error getting alert info: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 POLICE DASHBOARD API TEST COMPLETED")

if __name__ == "__main__":
    print("🚔 Smart Tourist Safety System - Police Dashboard API Test")
    print(f"🕐 Test Time: {datetime.now()}")
    print("\nNote: Make sure the server is running at http://localhost:8000")
    print("Note: This test uses mock police dashboard URL (will show connection error - that's expected)")
    
    asyncio.run(test_police_dashboard_api())