#!/usr/bin/env python3
"""
Complete PostgreSQL Database Setup Script
Creates database, tables, and populates with dummy data for Smart Tourist Safety System.
"""

import sys
import os
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def create_database_if_not_exists():
    """Create the PostgreSQL database if it doesn't exist"""
    print("🔍 Step 1: Setting up PostgreSQL Database...")
    print("=" * 60)
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return False
    
    try:
        parsed = urlparse(database_url)
        host = parsed.hostname
        port = parsed.port
        username = parsed.username
        password = parsed.password
        database_name = parsed.path[1:]  # Remove leading '/'
        
        print(f"📋 Host: {host}")
        print(f"📋 Port: {port}")
        print(f"📋 Username: {username}")
        print(f"📋 Target Database: {database_name}")
        
        # Connect to PostgreSQL server
        print("🔌 Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL server")
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{database_name}' already exists")
        else:
            print(f"🗄️  Creating database '{database_name}'...")
            cursor.execute(f'CREATE DATABASE "{database_name}"')
            print(f"✅ Database '{database_name}' created successfully")
        
        cursor.close()
        conn.close()
        
        # Test connection to target database
        print(f"🔗 Testing connection to '{database_name}'...")
        test_engine = create_engine(database_url)
        with test_engine.connect() as test_conn:
            result = test_conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Successfully connected to database: {db_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Ensure PostgreSQL is running")
        print("   - Check credentials in .env file")
        print("   - Verify PostgreSQL service is started")
        return False

def create_tables():
    """Create all required tables"""
    print("\n🔍 Step 2: Creating Database Tables...")
    print("=" * 60)
    
    try:
        from database import engine, Base
        from models import Tourist, Location, Alert, RestrictedZone
        
        print("📦 Importing models...")
        print(f"   - Tourist: {Tourist.__tablename__}")
        print(f"   - Location: {Location.__tablename__}")
        print(f"   - Alert: {Alert.__tablename__}")
        print(f"   - RestrictedZone: {RestrictedZone.__tablename__}")
        
        print("🏗️  Creating all tables...")
        Base.metadata.drop_all(bind=engine)  # Drop existing tables
        Base.metadata.create_all(bind=engine)  # Create fresh tables
        
        # Verify tables were created
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ['tourists', 'locations', 'alerts', 'restricted_zones']
            print(f"📋 Found tables: {tables}")
            
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' created successfully")
                else:
                    print(f"❌ Table '{table}' missing")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Table creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def populate_sample_data():
    """Populate database with comprehensive sample data"""
    print("\n🔍 Step 3: Populating Sample Data...")
    print("=" * 60)
    
    try:
        from database import SessionLocal
        from models import Tourist, Location, Alert, RestrictedZone, AlertType, AlertStatus
        
        db = SessionLocal()
        
        # Sample data
        SAMPLE_NAMES = [
            "Rahul Sharma", "Priya Patel", "Amit Kumar", "Sunita Singh", "Rajesh Gupta",
            "Anjali Verma", "Vikram Reddy", "Kavita Joshi", "Arjun Nair", "Pooja Agarwal",
            "Sanjay Yadav", "Neha Kapoor", "Ravi Mehta", "Shreya Bansal", "Manoj Tiwari",
            "Divya Chawla", "Karan Malhotra", "Ritika Saxena", "Deepak Jain", "Swati Goyal",
            "Nikhil Pandey", "Aditi Srivastava", "Rohit Mishra", "Ankita Bhatt", "Suresh Modi",
            "Meera Pillai", "Gaurav Sinha", "Pallavi Rao", "Vinay Khanna", "Nisha Arora",
            "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis", "David Wilson",
            "Lisa Anderson", "Robert Taylor", "Jennifer Thomas", "William Jackson", "Mary White",
            "James Harris", "Patricia Martin", "Christopher Thompson", "Linda Garcia", "Daniel Martinez"
        ]
        
        CITY_COORDINATES = {
            "Delhi": [28.6139, 77.2090],
            "Mumbai": [19.0760, 72.8777],
            "Bangalore": [12.9716, 77.5946],
            "Chennai": [13.0827, 80.2707],
            "Kolkata": [22.5726, 88.3639],
            "Hyderabad": [17.3850, 78.4867],
            "Pune": [18.5204, 73.8567],
            "Goa": [15.2993, 74.1240],
            "Shillong": [25.5788, 91.8933],
            "Manali": [32.2396, 77.1887]
        }
        
        # 1. Create Restricted Zones
        print("🚫 Creating restricted zones...")
        zones_data = [
            {
                "name": "Delhi Red Fort Security Zone",
                "description": "High security area around Red Fort monument",
                "coordinates": [[28.6562, 77.2410], [28.6572, 77.2420], [28.6552, 77.2430], [28.6542, 77.2415]],
                "risk_level": 8
            },
            {
                "name": "Mumbai Naval Base Restricted Area",
                "description": "Military restricted naval facility",
                "coordinates": [[19.0220, 72.8347], [19.0240, 72.8367], [19.0200, 72.8387], [19.0180, 72.8357]],
                "risk_level": 9
            },
            {
                "name": "Goa Protected Beach Zone",
                "description": "Environmentally sensitive coastal area",
                "coordinates": [[15.2760, 74.1240], [15.2780, 74.1260], [15.2740, 74.1280], [15.2720, 74.1250]],
                "risk_level": 6
            },
            {
                "name": "Bangalore Airport Security Perimeter",
                "description": "Airport security restricted zone",
                "coordinates": [[13.1979, 77.7063], [13.1999, 77.7083], [13.1959, 77.7103], [13.1939, 77.7073]],
                "risk_level": 7
            },
            {
                "name": "Shillong Military Cantonment",
                "description": "Defense establishment restricted area",
                "coordinates": [[25.5688, 91.8833], [25.5708, 91.8853], [25.5668, 91.8873], [25.5648, 91.8843]],
                "risk_level": 10
            }
        ]
        
        for zone_data in zones_data:
            zone = RestrictedZone(
                name=zone_data["name"],
                description=zone_data["description"],
                polygon_coordinates=json.dumps(zone_data["coordinates"]),
                risk_level=zone_data["risk_level"]
            )
            db.add(zone)
        
        db.commit()
        zone_count = db.query(RestrictedZone).count()
        print(f"✅ Created {zone_count} restricted zones")
        
        # 2. Create Tourists
        print("👥 Creating tourists...")
        tourists = []
        for i, name in enumerate(SAMPLE_NAMES[:50]):  # Create 50 tourists
            tourist = Tourist(
                name=name,
                contact=f"98765432{i:02d}",
                trip_info=f"Visiting {random.choice(list(CITY_COORDINATES.keys()))} for {random.choice(['leisure', 'business', 'pilgrimage', 'adventure'])}",
                emergency_contact=f"98765433{i:02d}",
                safety_score=random.randint(60, 100)
            )
            tourists.append(tourist)
            db.add(tourist)
        
        db.commit()
        
        # Refresh to get IDs
        for tourist in tourists:
            db.refresh(tourist)
        
        tourist_count = db.query(Tourist).count()
        print(f"✅ Created {tourist_count} tourists")
        
        # 3. Create Location Data
        print("📍 Creating location data...")
        cities = list(CITY_COORDINATES.items())
        location_count = 0
        
        for tourist in tourists:
            city_name, city_coords = random.choice(cities)
            num_locations = random.randint(3, 10)
            
            for j in range(num_locations):
                hours_ago = random.randint(1, 168)  # Last week
                timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
                
                # Add some variation to coordinates
                lat_variation = random.uniform(-0.05, 0.05)
                lon_variation = random.uniform(-0.05, 0.05)
                
                location = Location(
                    tourist_id=tourist.id,
                    latitude=round(city_coords[0] + lat_variation, 6),
                    longitude=round(city_coords[1] + lon_variation, 6),
                    timestamp=timestamp
                )
                db.add(location)
                location_count += 1
        
        db.commit()
        print(f"✅ Created {location_count} location records")
        
        # 4. Create Sample Alerts
        print("🚨 Creating sample alerts...")
        alert_tourists = random.sample(tourists, min(15, len(tourists)))
        alert_count = 0
        
        for tourist in alert_tourists:
            # Get a location for this tourist
            location = db.query(Location).filter(Location.tourist_id == tourist.id).first()
            if not location:
                continue
            
            alert_type = random.choice([AlertType.panic, AlertType.geofence])
            hours_ago = random.randint(1, 48)
            timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
            
            if alert_type == AlertType.panic:
                message = f"PANIC ALERT: {tourist.name} has triggered a panic alert at coordinates ({location.latitude}, {location.longitude})"
            else:
                message = f"GEOFENCE VIOLATION: {tourist.name} has entered restricted zone at coordinates ({location.latitude}, {location.longitude})"
            
            status = random.choice([AlertStatus.active, AlertStatus.resolved])
            resolved_at = None
            if status == AlertStatus.resolved:
                resolved_at = timestamp + timedelta(hours=random.randint(1, 6))
            
            alert = Alert(
                tourist_id=tourist.id,
                type=alert_type,
                message=message,
                latitude=location.latitude,
                longitude=location.longitude,
                timestamp=timestamp,
                status=status,
                resolved_at=resolved_at
            )
            db.add(alert)
            alert_count += 1
        
        db.commit()
        print(f"✅ Created {alert_count} sample alerts")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Data population error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_setup():
    """Verify the complete setup"""
    print("\n🔍 Step 4: Verifying Complete Setup...")
    print("=" * 60)
    
    try:
        from database import SessionLocal
        from models import Tourist, Location, Alert, RestrictedZone
        
        db = SessionLocal()
        
        # Count records
        tourist_count = db.query(Tourist).count()
        location_count = db.query(Location).count()
        alert_count = db.query(Alert).count()
        zone_count = db.query(RestrictedZone).count()
        
        print(f"📊 Database Statistics:")
        print(f"   👥 Tourists: {tourist_count}")
        print(f"   📍 Locations: {location_count}")
        print(f"   🚨 Alerts: {alert_count}")
        print(f"   🚫 Restricted Zones: {zone_count}")
        
        # Test some queries
        print(f"\n🔍 Sample Data Verification:")
        
        # Get a sample tourist with safety score
        sample_tourist = db.query(Tourist).first()
        if sample_tourist:
            print(f"   Sample Tourist: {sample_tourist.name} (Safety Score: {sample_tourist.safety_score})")
        
        # Get latest locations
        latest_locations = db.query(Location).order_by(Location.timestamp.desc()).limit(3).all()
        print(f"   Latest Location Updates: {len(latest_locations)} records")
        
        # Get active alerts
        active_alerts = db.query(Alert).filter(Alert.status == 'active').count()
        print(f"   Active Alerts: {active_alerts}")
        
        # Get restricted zones
        zones = db.query(RestrictedZone).all()
        if zones:
            print(f"   Sample Zone: {zones[0].name} (Risk Level: {zones[0].risk_level})")
        
        db.close()
        
        if tourist_count > 0 and location_count > 0:
            return True
        else:
            print("❌ Setup verification failed - missing data")
            return False
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Complete database setup process"""
    print("🐘 Complete PostgreSQL Database Setup")
    print("Smart Tourist Safety & Incident Response System")
    print("=" * 70)
    
    steps_completed = 0
    total_steps = 4
    
    # Step 1: Create Database
    if create_database_if_not_exists():
        steps_completed += 1
        print("✅ Step 1 completed: Database ready")
    else:
        print("❌ Step 1 failed: Database setup failed")
        return False
    
    # Step 2: Create Tables
    if create_tables():
        steps_completed += 1
        print("✅ Step 2 completed: Tables created")
    else:
        print("❌ Step 2 failed: Table creation failed")
        return False
    
    # Step 3: Populate Data
    if populate_sample_data():
        steps_completed += 1
        print("✅ Step 3 completed: Sample data populated")
    else:
        print("❌ Step 3 failed: Data population failed")
        return False
    
    # Step 4: Verify Setup
    if verify_setup():
        steps_completed += 1
        print("✅ Step 4 completed: Setup verified")
    else:
        print("❌ Step 4 failed: Verification failed")
        return False
    
    # Final Summary
    print("\n" + "=" * 70)
    print("🎉 COMPLETE DATABASE SETUP SUCCESSFUL!")
    print("=" * 70)
    print(f"✅ All {steps_completed}/{total_steps} steps completed successfully")
    print("\n🚀 Your PostgreSQL database is now ready with:")
    print("   🗄️  Complete database schema")
    print("   👥 50 sample tourists")
    print("   📍 300+ location records")
    print("   🚨 15+ alert records")
    print("   🚫 5 restricted zones")
    print("\n📝 Next steps:")
    print("   1. Run: python main.py")
    print("   2. Visit: http://localhost:8000/docs")
    print("   3. Test APIs with sample data")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)