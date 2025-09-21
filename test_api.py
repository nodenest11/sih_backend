import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.json()}")
    return response.status_code == 200

def test_register_tourist():
    """Test tourist registration"""
    tourist_data = {
        "name": "Test User",
        "contact": "9876543210",
        "trip_info": "Testing the API",
        "emergency_contact": "9876543211"
    }
    
    response = requests.post(f"{BASE_URL}/tourists/register", json=tourist_data)
    print(f"Tourist registration: {response.status_code}")
    if response.status_code == 201:
        print(f"Tourist created: {response.json()}")
        return response.json()['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_update_location(tourist_id):
    """Test location update"""
    location_data = {
        "tourist_id": tourist_id,
        "latitude": 28.61,
        "longitude": 77.23
    }
    
    response = requests.post(f"{BASE_URL}/locations/update", json=location_data)
    print(f"Location update: {response.status_code}")
    if response.status_code == 201:
        print(f"Location updated: {response.json()}")
    else:
        print(f"Error: {response.json()}")

def test_panic_alert(tourist_id):
    """Test panic alert creation"""
    alert_data = {
        "tourist_id": tourist_id,
        "latitude": 28.61,
        "longitude": 77.23
    }
    
    response = requests.post(f"{BASE_URL}/alerts/panic", json=alert_data)
    print(f"Panic alert: {response.status_code}")
    if response.status_code == 201:
        print(f"Alert created: {response.json()}")
        return response.json()['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_get_alerts():
    """Test getting alerts"""
    response = requests.get(f"{BASE_URL}/alerts/")
    print(f"Get alerts: {response.status_code}")
    if response.status_code == 200:
        alerts = response.json()
        print(f"Found {len(alerts)} alerts")
        if alerts:
            print(f"First alert: {alerts[0]}")
    else:
        print(f"Error: {response.json()}")

def main():
    print("Testing Smart Tourist Safety API...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("Health check failed. Is the server running?")
        return
    
    print("\n" + "=" * 50)
    
    # Test tourist registration
    tourist_id = test_register_tourist()
    if not tourist_id:
        print("Tourist registration failed")
        return
    
    print("\n" + "=" * 50)
    
    # Test location update
    test_update_location(tourist_id)
    
    print("\n" + "=" * 50)
    
    # Test panic alert
    alert_id = test_panic_alert(tourist_id)
    
    print("\n" + "=" * 50)
    
    # Test getting alerts
    test_get_alerts()
    
    print("\n" + "=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    main()