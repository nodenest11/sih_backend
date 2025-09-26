#!/usr/bin/env python3
"""
Insert dummy data into the Smart Tourist Safety database
- Creates sample tourists with Indian names
- Adds location tracking data
- Creates sample alerts for testing
- Initializes restricted zones
"""

import requests
import json
import random
import time
from datetime import datetime, timedelta

# API Base URL
BASE_URL = "http://localhost:8000"

# Indian names for dummy data
INDIAN_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Shaurya", "Atharv", "Advik", "Pranav", "Vedant", "Kabir", "Aryan", "Yash", "Dev", "Rudra",
    "Ananya", "Diya", "Priya", "Anika", "Kavya", "Aadhya", "Sara", "Pari", "Fatima", "Ira",
    "Riya", "Myra", "Aayushi", "Ishita", "Khushi", "Anushka", "Kiara", "Saanvi", "Aarohi", "Shanaya"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Agarwal", "Mishra", "Singh", "Kumar", "Jain", "Bansal", "Garg",
    "Arora", "Chopra", "Malhotra", "Kapoor", "Bhatia", "Sood", "Sethi", "Khanna", "Goyal", "Jindal",
    "Mittal", "Agrawal", "Saxena", "Srivastava", "Tiwari", "Pandey", "Yadav", "Chauhan", "Rajput", "Joshi"
]

# Popular Indian tourist destinations with coordinates
TOURIST_LOCATIONS = {
    "New Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Agra": {"lat": 27.1767, "lon": 78.0081},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Goa": {"lat": 15.2993, "lon": 74.1240},
    "Kerala": {"lat": 10.8505, "lon": 76.2711},
    "Udaipur": {"lat": 24.5854, "lon": 73.7125},
    "Varanasi": {"lat": 25.3176, "lon": 82.9739},
    "Rishikesh": {"lat": 30.0869, "lon": 78.2676},
    "Manali": {"lat": 32.2432, "lon": 77.1892},
    "Shimla": {"lat": 31.1048, "lon": 77.1734},
    "Darjeeling": {"lat": 27.0360, "lon": 88.2627},
    "Amritsar": {"lat": 31.6340, "lon": 74.8723},
    "Jodhpur": {"lat": 26.2389, "lon": 73.0243},
    "Hampi": {"lat": 15.3350, "lon": 76.4600},
    "Shillong": {"lat": 25.5788, "lon": 91.8933},
}

# Trip purposes
TRIP_PURPOSES = [
    "Golden Triangle tour (Delhi-Agra-Jaipur)",
    "Goa beach holiday",
    "Kerala backwaters cruise", 
    "Rajasthan heritage tour",
    "Himachal Pradesh adventure trip",
    "Religious pilgrimage to Varanasi",
    "Kashmir valley tour",
    "North East India exploration",
    "Mumbai city break",
    "Tamil Nadu temple tour",
    "Karnataka cultural journey",
    "Yoga retreat in Rishikesh",
    "Wildlife safari in Jim Corbett",
    "Ladakh motorcycle expedition",
    "Andaman Islands beach vacation"
]

def generate_phone_number():
    """Generate a realistic Indian phone number"""
    first_digit = random.choice(['6', '7', '8', '9'])
    remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return first_digit + remaining_digits

def generate_tourist():
    """Generate a random Indian tourist"""
    first_name = random.choice(INDIAN_FIRST_NAMES)
    last_name = random.choice(INDIAN_LAST_NAMES)
    name = f"{first_name} {last_name}"
    
    return {
        "name": name,
        "contact": generate_phone_number(),
        "trip_info": random.choice(TRIP_PURPOSES),
        "emergency_contact": generate_phone_number()
    }

def add_location_variation(lat, lon, variation=0.01):
    """Add small random variation to coordinates"""
    return {
        "lat": lat + random.uniform(-variation, variation),
        "lon": lon + random.uniform(-variation, variation)
    }

def main():
    print("🚀 Starting dummy data insertion...")
    
    # Step 1: Initialize database with restricted zones
    print("\n📍 Initializing restricted zones...")
    try:
        response = requests.post(f"{BASE_URL}/admin/initialize-database")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created {result['restricted_zones_created']} restricted zones")
        else:
            print(f"⚠️  Warning: {response.text}")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    
    # Step 2: Create tourists
    print(f"\n👥 Creating 25 sample tourists...")
    tourists = []
    
    for i in range(25):
        tourist_data = generate_tourist()
        try:
            response = requests.post(f"{BASE_URL}/tourists/register", json=tourist_data)
            if response.status_code == 201:
                tourist = response.json()
                tourists.append(tourist)
                print(f"✅ Created tourist: {tourist['name']} (ID: {tourist['id']})")
            else:
                print(f"❌ Failed to create tourist {i+1}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating tourist {i+1}: {e}")
    
    print(f"📊 Successfully created {len(tourists)} tourists")
    
    # Step 3: Add location data for tourists
    print(f"\n📍 Adding location data for tourists...")
    location_count = 0
    
    for tourist in tourists:
        # Each tourist gets 2-5 location updates at different places
        num_locations = random.randint(2, 5)
        
        for _ in range(num_locations):
            location_name = random.choice(list(TOURIST_LOCATIONS.keys()))
            base_location = TOURIST_LOCATIONS[location_name]
            location = add_location_variation(base_location["lat"], base_location["lon"])
            
            location_data = {
                "tourist_id": tourist["id"],
                "latitude": location["lat"],
                "longitude": location["lon"]
            }
            
            try:
                response = requests.post(f"{BASE_URL}/locations/update", json=location_data)
                if response.status_code == 201:
                    location_count += 1
                    print(f"📍 Added location for {tourist['name']} at {location_name}")
                else:
                    print(f"❌ Failed to add location for tourist {tourist['id']}")
                    
                # Small delay to create realistic timestamps
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Error adding location: {e}")
    
    print(f"📊 Added {location_count} location records")
    
    # Step 4: Create some sample alerts
    print(f"\n🚨 Creating sample alerts...")
    alert_count = 0
    
    # Create 5 panic alerts
    for i in range(5):
        tourist = random.choice(tourists)
        location_name = random.choice(list(TOURIST_LOCATIONS.keys()))
        base_location = TOURIST_LOCATIONS[location_name]
        location = add_location_variation(base_location["lat"], base_location["lon"])
        
        alert_data = {
            "tourist_id": tourist["id"],
            "latitude": location["lat"],
            "longitude": location["lon"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/alerts/panic", json=alert_data)
            if response.status_code == 201:
                alert_count += 1
                print(f"🚨 Created panic alert for {tourist['name']} at {location_name}")
        except Exception as e:
            print(f"❌ Error creating panic alert: {e}")
    
    # Create 3 geofence alerts
    restricted_zones = [
        {"name": "Delhi Red Fort Restricted Area", "lat": 28.6571, "lon": 77.2425},
        {"name": "Goa Beach Danger Zone", "lat": 15.3001, "lon": 74.1250},
        {"name": "Shillong Restricted Military Zone", "lat": 25.5794, "lon": 91.8941}
    ]
    
    for zone in restricted_zones:
        tourist = random.choice(tourists)
        
        alert_data = {
            "tourist_id": tourist["id"],
            "latitude": zone["lat"],
            "longitude": zone["lon"],
            "zone_name": zone["name"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/alerts/geofence", json=alert_data)
            if response.status_code == 201:
                alert_count += 1
                print(f"⚠️  Created geofence alert for {tourist['name']} at {zone['name']}")
        except Exception as e:
            print(f"❌ Error creating geofence alert: {e}")
    
    print(f"📊 Created {alert_count} alerts")
    
    # Step 5: Show summary
    print(f"\n📈 Database Population Summary:")
    print(f"👥 Tourists: {len(tourists)}")
    print(f"📍 Locations: {location_count}")
    print(f"🚨 Alerts: {alert_count}")
    print(f"🏛️  Restricted Zones: 3")
    
    print(f"\n✅ Database successfully populated with dummy data!")
    print(f"🌐 You can now test the API endpoints:")
    print(f"   - View API docs: http://localhost:8000/docs")
    print(f"   - Get all alerts: http://localhost:8000/alerts")
    print(f"   - Get all locations: http://localhost:8000/locations/all")
    print(f"   - Health check: http://localhost:8000/admin/health")

if __name__ == "__main__":
    main()