from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Tourist, Location, Alert, RestrictedZone, AlertType, AlertStatus
from datetime import datetime, timedelta
import random
import json

# Sample data for seeding
SAMPLE_NAMES = [
    "Rahul Sharma", "Priya Patel", "Amit Kumar", "Sunita Singh", "Rajesh Gupta",
    "Anjali Verma", "Vikram Reddy", "Kavita Joshi", "Arjun Nair", "Pooja Agarwal",
    "Sanjay Yadav", "Neha Kapoor", "Ravi Mehta", "Shreya Bansal", "Manoj Tiwari",
    "Divya Chawla", "Karan Malhotra", "Ritika Saxena", "Deepak Jain", "Swati Goyal",
    "Nikhil Pandey", "Aditi Srivastava", "Rohit Mishra", "Ankita Bhatt", "Suresh Modi",
    "Meera Pillai", "Gaurav Sinha", "Pallavi Rao", "Vinay Khanna", "Nisha Arora",
    "Ashish Goel", "Rekha Das", "Himanshu Jha", "Shilpa Bose", "Yogesh Desai",
    "Aarti Dutta", "Harish Lal", "Seema Roy", "Tarun Shah", "Vandana Kulkarni",
    "Sachin Bhosle", "Rashmi Iyer", "Mukesh Aher", "Vaishali Naik", "Pramod Sawant",
    "Kajal Thakur", "Vishal Chopra", "Ritu Sethi", "Abhishek Gill", "Manisha Dhawan",
    "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis", "David Wilson",
    "Lisa Anderson", "Robert Taylor", "Jennifer Thomas", "William Jackson", "Mary White",
    "James Harris", "Patricia Martin", "Christopher Thompson", "Linda Garcia", "Daniel Martinez",
    "Elizabeth Robinson", "Matthew Clark", "Barbara Rodriguez", "Anthony Lewis", "Susan Lee",
    "Mark Walker", "Jessica Hall", "Steven Allen", "Karen Young", "Andrew King",
    "Nancy Wright", "Joshua Lopez", "Betty Hill", "Kenneth Scott", "Helen Green",
    "Paul Adams", "Sandra Baker", "Ryan Gonzalez", "Donna Nelson", "Gary Carter",
    "Carol Mitchell", "Nicholas Perez", "Ruth Roberts", "Jonathan Turner", "Sharon Phillips",
    "Stephen Campbell", "Michelle Parker", "Larry Evans", "Laura Edwards", "Justin Collins",
    "Kimberly Stewart", "Brandon Sanchez", "Deborah Morris", "Jacob Rogers", "Dorothy Reed",
    "Tyler Cook", "Lisa Morgan", "Alexander Bailey", "Nancy Rivera", "Nathan Cooper",
    "Karen Richardson", "Zachary Cox", "Betty Howard", "Kyle Ward", "Helen Torres"
]

# Location coordinates for different cities in India
CITY_COORDINATES = {
    "Delhi": [28.6139, 77.2090],
    "Mumbai": [19.0760, 72.8777],
    "Bangalore": [12.9716, 77.5946],
    "Chennai": [13.0827, 80.2707],
    "Kolkata": [22.5726, 88.3639],
    "Hyderabad": [17.3850, 78.4867],
    "Pune": [18.5204, 73.8567],
    "Ahmedabad": [23.0225, 72.5714],
    "Jaipur": [26.9124, 75.7873],
    "Goa": [15.2993, 74.1240],
    "Shillong": [25.5788, 91.8933],
    "Manali": [32.2396, 77.1887],
    "Rishikesh": [30.0869, 78.2676],
    "Varanasi": [25.3176, 82.9739],
    "Kochi": [9.9312, 76.2673]
}

# Sample emergency contacts
EMERGENCY_CONTACTS = [
    "9876543210", "9876543211", "9876543212", "9876543213", "9876543214",
    "9876543215", "9876543216", "9876543217", "9876543218", "9876543219"
]

def generate_phone_number():
    """Generate a random Indian phone number"""
    return f"{''.join([str(random.randint(0, 9)) for _ in range(10)])}"

def get_random_coordinates_near_city(city_coords, radius_km=5):
    """Generate random coordinates within radius of a city"""
    lat, lon = city_coords
    # Convert km to degrees (rough approximation)
    lat_range = radius_km / 111.0
    lon_range = radius_km / (111.0 * abs(lat))
    
    new_lat = lat + random.uniform(-lat_range, lat_range)
    new_lon = lon + random.uniform(-lon_range, lon_range)
    
    return round(new_lat, 6), round(new_lon, 6)

def create_restricted_zones(db: Session):
    """Create sample restricted zones"""
    zones = [
        {
            "name": "Delhi Red Fort Restricted Area",
            "description": "Security sensitive area around Red Fort",
            "coordinates": [
                [28.6562, 77.2410],
                [28.6572, 77.2420],
                [28.6552, 77.2430],
                [28.6542, 77.2415]
            ],
            "risk_level": 8
        },
        {
            "name": "Mumbai Naval Dock Yard",
            "description": "Military restricted zone",
            "coordinates": [
                [18.9220, 72.8347],
                [18.9240, 72.8367],
                [18.9200, 72.8387],
                [18.9180, 72.8357]
            ],
            "risk_level": 9
        },
        {
            "name": "Goa Restricted Beach Area",
            "description": "Environmentally protected beach zone",
            "coordinates": [
                [15.2760, 74.1240],
                [15.2780, 74.1260],
                [15.2740, 74.1280],
                [15.2720, 74.1250]
            ],
            "risk_level": 6
        },
        {
            "name": "Bangalore Airport Security Zone",
            "description": "Airport perimeter security area",
            "coordinates": [
                [13.1979, 77.7063],
                [13.1999, 77.7083],
                [13.1959, 77.7103],
                [13.1939, 77.7073]
            ],
            "risk_level": 7
        },
        {
            "name": "Shillong Military Cantonment",
            "description": "Military cantonment restricted area",
            "coordinates": [
                [25.5688, 91.8833],
                [25.5708, 91.8853],
                [25.5668, 91.8873],
                [25.5648, 91.8843]
            ],
            "risk_level": 10
        }
    ]
    
    for zone_data in zones:
        zone = RestrictedZone(
            name=zone_data["name"],
            description=zone_data["description"],
            polygon_coordinates=json.dumps(zone_data["coordinates"]),
            risk_level=zone_data["risk_level"]
        )
        db.add(zone)
    
    db.commit()
    print(f"Created {len(zones)} restricted zones")

def create_sample_tourists(db: Session, count=100):
    """Create sample tourists"""
    cities = list(CITY_COORDINATES.keys())
    
    for i in range(count):
        # Select random city for tourist's trip
        destination_city = random.choice(cities)
        
        tourist = Tourist(
            name=SAMPLE_NAMES[i],
            contact=generate_phone_number(),
            trip_info=f"Visiting {destination_city} for {random.choice(['leisure', 'business', 'pilgrimage', 'adventure', 'family visit'])}",
            emergency_contact=random.choice(EMERGENCY_CONTACTS),
            safety_score=random.randint(60, 100)  # Start with decent safety scores
        )
        
        db.add(tourist)
    
    db.commit()
    print(f"Created {count} sample tourists")

def create_sample_locations(db: Session):
    """Create sample location data for tourists"""
    tourists = db.query(Tourist).all()
    cities = list(CITY_COORDINATES.items())
    
    for tourist in tourists:
        # Each tourist gets 3-8 location updates
        num_locations = random.randint(3, 8)
        
        # Pick a random city for this tourist's journey
        city_name, city_coords = random.choice(cities)
        
        # Create location updates over the past few days
        for i in range(num_locations):
            # Generate timestamps going backwards in time
            hours_ago = random.randint(1, 72)  # Last 3 days
            timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
            
            # Generate coordinates near the chosen city
            lat, lon = get_random_coordinates_near_city(city_coords)
            
            location = Location(
                tourist_id=tourist.id,
                latitude=lat,
                longitude=lon,
                timestamp=timestamp
            )
            
            db.add(location)
    
    db.commit()
    print(f"Created location data for {len(tourists)} tourists")

def create_sample_alerts(db: Session):
    """Create some sample alerts"""
    tourists = db.query(Tourist).all()
    
    # Create 10-15 random alerts
    num_alerts = random.randint(10, 15)
    selected_tourists = random.sample(tourists, min(num_alerts, len(tourists)))
    
    for tourist in selected_tourists:
        # Get a recent location for this tourist
        location = db.query(Location).filter(
            Location.tourist_id == tourist.id
        ).order_by(Location.timestamp.desc()).first()
        
        if not location:
            continue
        
        alert_type = random.choice([AlertType.panic, AlertType.geofence])
        hours_ago = random.randint(1, 24)
        timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
        
        if alert_type == AlertType.panic:
            message = f"PANIC ALERT: {tourist.name} has triggered a panic alert"
        else:
            message = f"GEOFENCE VIOLATION: {tourist.name} has entered a restricted zone"
        
        alert = Alert(
            tourist_id=tourist.id,
            type=alert_type,
            message=message,
            latitude=location.latitude,
            longitude=location.longitude,
            timestamp=timestamp,
            status=random.choice([AlertStatus.active, AlertStatus.resolved])
        )
        
        if alert.status == AlertStatus.resolved:
            alert.resolved_at = timestamp + timedelta(hours=random.randint(1, 6))
        
        db.add(alert)
    
    db.commit()
    print(f"Created {num_alerts} sample alerts")

def seed_database():
    """Main function to seed the database with sample data"""
    print("Starting database seeding...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_tourists = db.query(Tourist).count()
        if existing_tourists > 0:
            print(f"Database already has {existing_tourists} tourists. Skipping seeding.")
            return
        
        # Create sample data
        create_restricted_zones(db)
        create_sample_tourists(db, 100)
        create_sample_locations(db)
        create_sample_alerts(db)
        
        print("Database seeding completed successfully!")
        
        # Print summary
        tourist_count = db.query(Tourist).count()
        location_count = db.query(Location).count()
        alert_count = db.query(Alert).count()
        zone_count = db.query(RestrictedZone).count()
        
        print(f"\nSummary:")
        print(f"- Tourists: {tourist_count}")
        print(f"- Locations: {location_count}")
        print(f"- Alerts: {alert_count}")
        print(f"- Restricted Zones: {zone_count}")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()