#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script
Creates the required database for the Smart Tourist Safety system.
"""

import sys
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def create_database():
    """Create the tourist_safety_db database if it doesn't exist"""
    print("🔍 Setting up PostgreSQL Database...")
    print("=" * 50)
    
    # Get database URL and parse it
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return False
    
    # Parse the database URL to get connection details
    # Format: postgresql://username:password@localhost:5432/database_name
    try:
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        host = parsed.hostname
        port = parsed.port
        username = parsed.username
        password = parsed.password
        database_name = parsed.path[1:]  # Remove leading '/'
        
        print(f"📋 Host: {host}")
        print(f"📋 Port: {port}")
        print(f"📋 Username: {username}")
        print(f"📋 Database: {database_name}")
        
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        return False
    
    try:
        print("🔌 Connecting to PostgreSQL server...")
        
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database='postgres'  # Connect to default postgres database
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
        
        # Test connection to the new database
        print(f"🔗 Testing connection to '{database_name}'...")
        test_engine = create_engine(database_url)
        with test_engine.connect() as test_conn:
            result = test_conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✅ Successfully connected to database: {db_name}")
        
        print("=" * 50)
        print("🎉 Database setup completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            print("❌ PostgreSQL server connection failed")
            print("💡 Please ensure PostgreSQL is installed and running")
            print("   Windows: Check if PostgreSQL service is running")
            print("   macOS: brew services start postgresql")
            print("   Linux: sudo systemctl start postgresql")
        else:
            print(f"❌ Database connection error: {e}")
        return False
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def setup_tables():
    """Create tables in the database"""
    print("\n🔍 Setting up Database Tables...")
    print("=" * 50)
    
    try:
        from database import engine, Base
        
        print("🏗️  Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
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
            print(f"📋 Created tables: {tables}")
            
            all_tables_exist = True
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' created")
                else:
                    print(f"❌ Table '{table}' missing")
                    all_tables_exist = False
            
            if all_tables_exist:
                print("=" * 50)
                print("🎉 All tables created successfully!")
                return True
            else:
                return False
                
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def main():
    """Main setup function"""
    print("🐘 PostgreSQL Database Setup for Smart Tourist Safety System")
    print("=" * 70)
    
    # Step 1: Create database
    if not create_database():
        print("\n❌ Database setup failed. Please check your PostgreSQL installation.")
        return False
    
    # Step 2: Create tables
    if not setup_tables():
        print("\n❌ Table creation failed.")
        return False
    
    print("\n" + "=" * 70)
    print("🎉 PostgreSQL setup completed successfully!")
    print("🚀 Your backend is now configured to use PostgreSQL exclusively.")
    print("\n📝 Next steps:")
    print("   1. Run: python test_postgresql.py  (to verify everything works)")
    print("   2. Run: python main.py  (to start the API server)")
    print("   3. Visit: http://localhost:8000/docs  (to test the API)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)