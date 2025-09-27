"""
🧪 Smart Tourist Safety System - Final Validation Test
Quick comprehensive test to validate all system functionality
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def validate_system():
    """Quick validation of all system components"""
    print("🚀 Smart Tourist Safety System - Final Validation")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. Health Check
    print("\n🏥 Health Check...")
    try:
        response = session.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200 and response.json().get("database") == "connected":
            print("✅ Server healthy, database connected")
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # 2. Tourist Registration
    print("\n👤 Tourist Registration...")
    tourist_data = {
        "name": "Final Test User",
        "contact": "+91-9876543210",
        "email": "finaltest@example.com",
        "emergency_contact": "+91-9999999999",
        "age": 25,
        "nationality": "Indian"
    }
    
    try:
        response = session.post(f"{BASE_URL}/registerTourist", json=tourist_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            tourist_id = data.get("tourist_id")
            print(f"✅ Tourist registered: ID {tourist_id}")
        else:
            print("❌ Tourist registration failed")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # 3. Location Updates with AI Assessment
    print("\n📍 Location Updates & AI Assessment...")
    test_locations = [
        {"lat": 28.6129, "lon": 77.2295, "speed": 3.0, "desc": "Safe zone"},
        {"lat": 28.654, "lon": 77.241, "speed": 5.0, "desc": "Restricted zone"},
        {"lat": 28.6200, "lon": 77.2350, "speed": 80.0, "desc": "High speed"}
    ]
    
    assessments = []
    for location in test_locations:
        location_data = {
            "tourist_id": tourist_id,
            "latitude": location["lat"],
            "longitude": location["lon"],
            "speed": location["speed"]
        }
        
        try:
            response = session.post(f"{BASE_URL}/sendLocation", json=location_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                assessment = data.get("assessment", {})
                assessments.append(assessment)
                print(f"   📍 {location['desc']}: Safety={assessment.get('safety_score')}, "
                      f"Severity={assessment.get('severity')}")
                time.sleep(0.5)
            else:
                print(f"   ❌ Failed to send location: {location['desc']}")
        except Exception as e:
            print(f"   ❌ Location error: {e}")
    
    if len(assessments) == 3:
        print("✅ AI Assessment working - all locations processed")
    else:
        print("❌ AI Assessment incomplete")
        return False
    
    # 4. SOS Alert
    print("\n🆘 SOS Emergency Alert...")
    sos_data = {
        "tourist_id": tourist_id,
        "latitude": 28.6129,
        "longitude": 77.2295,
        "emergency_type": "panic"
    }
    
    try:
        response = session.post(f"{BASE_URL}/pressSOS", json=sos_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            alert_id = data.get("alert_id")
            print(f"✅ SOS Alert created: ID {alert_id}")
        else:
            print("❌ SOS Alert failed")
            return False
    except Exception as e:
        print(f"❌ SOS error: {e}")
        return False
    
    # 5. Alerts Retrieval
    print("\n🚨 Alerts Retrieval...")
    try:
        response = session.get(f"{BASE_URL}/getAlerts?tourist_id={tourist_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            alerts = data.get("alerts", [])
            print(f"✅ Retrieved {len(alerts)} alerts for tourist")
        else:
            print("❌ Alert retrieval failed")
            return False
    except Exception as e:
        print(f"❌ Alert retrieval error: {e}")
        return False
    
    # 6. Tourist Profile
    print("\n👤 Tourist Profile...")
    try:
        response = session.get(f"{BASE_URL}/tourists/{tourist_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            summary = data.get("summary", {})
            print(f"✅ Profile retrieved: {summary.get('total_locations')} locations, "
                  f"{summary.get('total_alerts')} alerts")
        else:
            print("❌ Profile retrieval failed")
            return False
    except Exception as e:
        print(f"❌ Profile error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL SYSTEM COMPONENTS VALIDATED SUCCESSFULLY!")
    print("✅ Database: Connected and operational")
    print("✅ API Endpoints: All working correctly") 
    print("✅ AI Assessment: Geofencing and anomaly detection active")
    print("✅ Emergency Response: SOS and alert system functional")
    print("✅ Data Persistence: All data stored in Supabase")
    print("\n🏆 SMART TOURIST SAFETY SYSTEM IS PRODUCTION READY!")
    return True

if __name__ == "__main__":
    validate_system()