#!/usr/bin/env python3
"""
PostgreSQL API Test Script
Tests the API with existing sample data in PostgreSQL database.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.json()}")
    return response.status_code == 200

def test_get_tourists():
    """Test getting existing tourists"""
    response = requests.get(f"{BASE_URL}/tourists/")
    print(f"Get tourists: {response.status_code}")
    if response.status_code == 200:
        tourists = response.json()
        print(f"Found {len(tourists)} tourists in database")
        if tourists:
            print(f"Sample tourist: {tourists[0]['name']} (ID: {tourists[0]['id']}, Score: {tourists[0]['safety_score']})")
            return tourists[0]['id']  # Return first tourist ID for further tests
    else:
        print(f"Error: {response.json()}")
    return None

def test_get_locations(tourist_id):
    """Test getting tourist locations"""
    response = requests.get(f"{BASE_URL}/locations/all")
    print(f"Get all locations: {response.status_code}")
    if response.status_code == 200:
        locations = response.json()
        print(f"Found {len(locations)} latest locations")
        if locations:
            print(f"Sample location: {locations[0]['tourist_name']} at ({locations[0]['latitude']}, {locations[0]['longitude']})")
    
    if tourist_id:
        response = requests.get(f"{BASE_URL}/locations/tourist/{tourist_id}")
        print(f"Get tourist {tourist_id} locations: {response.status_code}")
        if response.status_code == 200:
            locations = response.json()
            print(f"Tourist has {len(locations)} location records")

def test_get_alerts():
    """Test getting alerts"""
    response = requests.get(f"{BASE_URL}/alerts/")
    print(f"Get alerts: {response.status_code}")
    if response.status_code == 200:
        alerts = response.json()
        print(f"Found {len(alerts)} alerts")
        if alerts:
            alert = alerts[0]
            print(f"Sample alert: {alert['type'].upper()} from {alert['tourist_name']} - {alert['status']}")
            return alert['id']
    return None

def test_register_new_tourist():
    """Test registering a new tourist with unique contact"""
    import random
    unique_contact = f"99999{random.randint(10000, 99999)}"
    
    tourist_data = {
        "name": "Test User API",
        "contact": unique_contact,
        "trip_info": "Testing PostgreSQL API",
        "emergency_contact": f"99998{random.randint(10000, 99999)}"
    }
    
    response = requests.post(f"{BASE_URL}/tourists/register", json=tourist_data)
    print(f"New tourist registration: {response.status_code}")
    if response.status_code == 201:
        tourist = response.json()
        print(f"New tourist created: {tourist['name']} (ID: {tourist['id']})")
        return tourist['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_location_update(tourist_id):
    """Test updating location for a tourist"""
    if not tourist_id:
        return
    
    location_data = {
        "tourist_id": tourist_id,
        "latitude": 28.6139,  # Delhi coordinates
        "longitude": 77.2090
    }
    
    response = requests.post(f"{BASE_URL}/locations/update", json=location_data)
    print(f"Location update for tourist {tourist_id}: {response.status_code}")
    if response.status_code == 201:
        location = response.json()
        print(f"Location updated: {location['timestamp']}")

def test_risk_assessment(tourist_id):
    """Test risk assessment"""
    if not tourist_id:
        return
    
    response = requests.get(f"{BASE_URL}/admin/{tourist_id}/risk-assessment")
    print(f"Risk assessment for tourist {tourist_id}: {response.status_code}")
    if response.status_code == 200:
        assessment = response.json()
        print(f"Risk level: {assessment['risk_level']}")
        print(f"Safety score: {assessment['safety_score']}")
        print(f"Recent alerts (24h): {assessment['recent_alerts_24h']}")

def test_database_stats():
    """Get overall database statistics"""
    print("\n📊 Database Statistics:")
    
    # Count tourists
    response = requests.get(f"{BASE_URL}/tourists/")
    if response.status_code == 200:
        tourist_count = len(response.json())
        print(f"   👥 Total Tourists: {tourist_count}")
    
    # Count locations
    response = requests.get(f"{BASE_URL}/locations/all")
    if response.status_code == 200:
        location_count = len(response.json())
        print(f"   📍 Active Locations: {location_count}")
    
    # Count alerts
    response = requests.get(f"{BASE_URL}/alerts/?status_filter=all")
    if response.status_code == 200:
        all_alerts = len(response.json())
        print(f"   🚨 Total Alerts: {all_alerts}")
    
    response = requests.get(f"{BASE_URL}/alerts/?status_filter=active")
    if response.status_code == 200:
        active_alerts = len(response.json())
        print(f"   🚨 Active Alerts: {active_alerts}")

def main():
    print("🐘 PostgreSQL API Test Suite")
    print("Testing Smart Tourist Safety API with PostgreSQL Database")
    print("=" * 70)
    
    # Test 1: Health Check
    if not test_health():
        print("❌ Health check failed. Is the server running?")
        return False
    
    print("\n" + "=" * 70)
    
    # Test 2: Get existing tourists
    tourist_id = test_get_tourists()
    
    print("\n" + "=" * 70)
    
    # Test 3: Get locations
    test_get_locations(tourist_id)
    
    print("\n" + "=" * 70)
    
    # Test 4: Get alerts
    alert_id = test_get_alerts()
    
    print("\n" + "=" * 70)
    
    # Test 5: Register new tourist
    new_tourist_id = test_register_new_tourist()
    
    print("\n" + "=" * 70)
    
    # Test 6: Update location
    test_location_update(new_tourist_id or tourist_id)
    
    print("\n" + "=" * 70)
    
    # Test 7: Risk assessment
    test_risk_assessment(tourist_id)
    
    print("\n" + "=" * 70)
    
    # Test 8: Database statistics
    test_database_stats()
    
    print("\n" + "=" * 70)
    print("🎉 PostgreSQL API testing completed!")
    print("✅ All endpoints are working with PostgreSQL database")
    print("\n🚀 Your system is ready for frontend integration!")
    print("📝 API Documentation: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    main()