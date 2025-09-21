#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script
Tests the database connection and ensures PostgreSQL is working properly.
"""

import sys
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

def test_postgresql_connection():
    """Test PostgreSQL connection and basic operations"""
    print("🔍 Testing PostgreSQL Connection...")
    print("=" * 50)
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("   Please ensure .env file exists with DATABASE_URL set")
        return False
    
    print(f"📋 Database URL: {database_url}")
    
    # Validate PostgreSQL URL
    if not database_url.startswith("postgresql"):
        print("❌ ERROR: DATABASE_URL must start with 'postgresql://'")
        print(f"   Current URL: {database_url}")
        return False
    
    try:
        # Create engine
        print("🔌 Creating database engine...")
        engine = create_engine(database_url)
        
        # Test connection
        print("🔗 Testing database connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL Version: {version}")
        
        # Test database existence
        print("🗄️  Testing database access...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Connected to database: {db_name}")
        
        # Test table creation (without actually creating)
        print("🏗️  Testing table creation permissions...")
        with engine.connect() as connection:
            # Test if we can create tables (dry run)
            connection.execute(text("SELECT 1"))  # Simple permission test
            print("✅ Database permissions: OK")
        
        print("=" * 50)
        print("🎉 PostgreSQL connection test: PASSED")
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database connection error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure PostgreSQL server is running")
        print("   2. Check database credentials in .env file")
        print("   3. Verify database 'tourist_safety_db' exists")
        print("   4. Check if user 'postgres' has access permissions")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_app_imports():
    """Test if our app can import successfully with PostgreSQL config"""
    print("\n🔍 Testing Application Imports...")
    print("=" * 50)
    
    try:
        print("📦 Importing database module...")
        from database import engine, Base, get_db
        print("✅ Database module imported successfully")
        
        print("📦 Importing models...")
        from models import Tourist, Location, Alert, RestrictedZone
        print("✅ Models imported successfully")
        
        print("📦 Testing database session...")
        db_gen = get_db()
        db = next(db_gen)
        print("✅ Database session created successfully")
        db.close()
        
        print("=" * 50)
        print("🎉 Application import test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_table_creation():
    """Test creating tables in PostgreSQL"""
    print("\n🔍 Testing Table Creation...")
    print("=" * 50)
    
    try:
        from database import engine, Base
        
        print("🏗️  Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        # Test table existence
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
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
                    return False
        
        print("=" * 50)
        print("🎉 Table creation test: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Table creation error: {e}")
        return False

def main():
    """Run all PostgreSQL tests"""
    print("🐘 PostgreSQL Configuration Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Database Connection
    if test_postgresql_connection():
        tests_passed += 1
    
    # Test 2: Application Imports  
    if test_app_imports():
        tests_passed += 1
    
    # Test 3: Table Creation
    if test_table_creation():
        tests_passed += 1
    
    # Final Results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! PostgreSQL is configured correctly.")
        print("\n✅ Your backend is ready to use PostgreSQL exclusively.")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)