#!/usr/bin/env python3
"""
Debug table creation script
"""

import sys
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect

load_dotenv()

def debug_table_creation():
    """Debug table creation process"""
    print("🔍 Debugging Table Creation...")
    print("=" * 50)
    
    try:
        # Import and check models
        print("📦 Importing models...")
        from models import Tourist, Location, Alert, RestrictedZone
        print("✅ Models imported successfully")
        
        # Print model table names
        print(f"📋 Tourist table: {Tourist.__tablename__}")
        print(f"📋 Location table: {Location.__tablename__}")
        print(f"📋 Alert table: {Alert.__tablename__}")
        print(f"📋 RestrictedZone table: {RestrictedZone.__tablename__}")
        
        # Import database components
        from database import engine, Base
        print("✅ Database components imported")
        
        # Check if Base has metadata
        print(f"📋 Base metadata tables: {list(Base.metadata.tables.keys())}")
        
        # Create tables with verbose output
        print("🏗️  Creating tables...")
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        # Check what was actually created
        inspector = inspect(engine)
        actual_tables = inspector.get_table_names()
        print(f"📋 Actual tables in database: {actual_tables}")
        
        # Try manual table creation if needed
        if not actual_tables:
            print("⚠️  No tables found, trying individual model creation...")
            Tourist.__table__.create(bind=engine, checkfirst=True)
            Location.__table__.create(bind=engine, checkfirst=True)
            Alert.__table__.create(bind=engine, checkfirst=True)
            RestrictedZone.__table__.create(bind=engine, checkfirst=True)
            
            # Check again
            actual_tables = inspector.get_table_names()
            print(f"📋 Tables after manual creation: {actual_tables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_table_creation()