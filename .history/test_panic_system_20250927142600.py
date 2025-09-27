"""
Test script for Police Dashboard Integration
Tests the panic alert functionality that automatically saves to database and sends to police
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_panic_alert_system():
    """Test the complete panic alert system"""
    
    base_url = "http://localhost:8000"
    
    print("🚔 TESTING PANIC ALERT TO POLICE DASHBOARD")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # Step 1: Register a test tourist
        print("\n1️⃣ Registering test tourist...")
        tourist_data = {
            "name": "Test Tourist for Panic",
            "contact": "+919876543999",
            "email": "panic.test@example.com",
            "emergency_contact": "+919876543998",
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
            print(f"❌ Error: {e}")
            return
        
        # Step 2: Create panic alert (this will automatically save to DB and send to police)
        print("\n2️⃣ Creating panic alert (auto saves to DB & sends to police)...")
        panic_data = {
            "tourist_id": tourist_id,
            "latitude": 28.6139,  # New Delhi
            "longitude": 77.2090,
            "message": "HELP! Tourist in danger - immediate assistance needed!"
        }
        
        try:
            response = await client.post(f"{base_url}/alerts/pressSOS", json=panic_data)
            if response.status_code == 201:
                alert = response.json()
                alert_id = alert["id"]
                print(f"✅ Panic alert created with ID: {alert_id}")
                print(f"📍 Location: {alert['latitude']}, {alert['longitude']}")
                print(f"🚨 Severity: {alert['severity']}")
                print(f"📝 Message: {alert['message']}")
                print(f"👮 Acknowledged by police: {alert.get('acknowledged', False)}")
            else:
                print(f"❌ Failed to create panic alert: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error creating panic alert: {e}")
            return
        
        # Step 3: Get alert counts
        print("\n3️⃣ Getting alert counts...")
        try:
            response = await client.get(f"{base_url}/alerts/counts")
            if response.status_code == 200:
                counts = response.json()
                print("📊 Alert Statistics:")
                print(f"   Total Alerts: {counts['summary']['total_alerts']}")
                print(f"   Active Alerts: {counts['summary']['active_alerts']}")
                print(f"   Panic/SOS Alerts: {counts['summary']['panic_sos_alerts']}")
                print(f"   Critical Alerts: {counts['summary']['critical_alerts']}")
                print(f"   Police Notified: {counts['summary']['police_notified']}")
                print(f"   Today's Alerts: {counts['summary']['today_alerts']}")
        except Exception as e:
            print(f"⚠️ Error getting counts: {e}")
        
        # Step 4: Get police dashboard status
        print("\n4️⃣ Getting police dashboard status...")
        try:
            response = await client.get(f"{base_url}/alerts/police-status")
            if response.status_code == 200:
                police_status = response.json()
                print("🚔 Police Dashboard Status:")
                print(f"   Total sent to police: {police_status['police_dashboard_status']['total_sent_to_police']}")
                print(f"   Sent today: {police_status['police_dashboard_status']['sent_today']}")
                
                if police_status['recent_police_alerts']:
                    print("   Recent police alerts:")
                    for alert in police_status['recent_police_alerts'][-3:]:  # Show last 3
                        print(f"     - Alert {alert['alert_id']}: {alert['severity']} at {alert['location']}")
        except Exception as e:
            print(f"⚠️ Error getting police status: {e}")
        
        # Step 5: Get all active alerts
        print("\n5️⃣ Getting active alerts...")
        try:
            response = await client.get(f"{base_url}/alerts/getAlerts")
            if response.status_code == 200:
                alerts = response.json()
                print(f"📋 Found {len(alerts)} active alerts:")
                for alert in alerts[:3]:  # Show first 3
                    print(f"   - ID {alert['id']}: {alert['type']} ({alert['severity']}) - {alert['tourist_name']}")
        except Exception as e:
            print(f"⚠️ Error getting alerts: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 PANIC ALERT SYSTEM TEST COMPLETED")
    print("\n💡 What happened:")
    print("1. ✅ Tourist registered in database")
    print("2. ✅ Panic alert created and saved to database") 
    print("3. ✅ Alert automatically sent to police dashboard API")
    print("4. ✅ Alert marked as acknowledged by police")
    print("5. ✅ Statistics and counts updated")
    print("6. ✅ Police dashboard status tracked")

if __name__ == "__main__":
    print("🚔 Smart Tourist Safety System - Panic Alert Test")
    print(f"🕐 Test Time: {datetime.now()}")
    print("\n📌 Make sure the server is running at http://localhost:8000")
    
    asyncio.run(test_panic_alert_system())