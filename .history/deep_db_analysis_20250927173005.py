#!/usr/bin/env python3
"""
🔬 Deep Database Connection Analysis
Comprehensive testing of Supabase connection and data access
"""

import os
import sys
import json
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv

print("🔬 DEEP DATABASE CONNECTION ANALYSIS")
print("=" * 60)

# Load environment variables
load_dotenv()

# Check environment variables first
print("📋 ENVIRONMENT VARIABLES CHECK:")
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")

print(f"SUPABASE_URL: {'✅ SET' if supabase_url else '❌ MISSING'}")
if supabase_url:
    print(f"  Value: {supabase_url}")

print(f"SUPABASE_SERVICE_KEY: {'✅ SET' if supabase_service_key else '❌ MISSING'}")
if supabase_service_key:
    print(f"  Length: {len(supabase_service_key)} characters")
    print(f"  Starts with: {supabase_service_key[:20]}...")

print(f"SUPABASE_ANON_KEY: {'✅ SET' if supabase_anon_key else '❌ MISSING'}")

if not supabase_url or not supabase_service_key:
    print("\n❌ CRITICAL: Missing Supabase credentials!")
    sys.exit(1)

print("\n🔌 SUPABASE CLIENT TEST:")

try:
    # Import and create Supabase client
    from supabase import create_client, Client
    print("✅ Supabase library imported successfully")
    
    # Create client
    supabase: Client = create_client(supabase_url, supabase_service_key)
    print("✅ Supabase client created successfully")
    
    print(f"✅ Client URL: {supabase.supabase_url}")
    print(f"✅ Client Key: {supabase.supabase_key[:20]}...")
    
except Exception as e:
    print(f"❌ Failed to create Supabase client: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n🏗️ DATABASE STRUCTURE TEST:")

# Test each table
tables_to_test = [
    "tourists",
    "locations", 
    "alerts",
    "safe_zones",
    "restricted_zones",
    "ai_assessments"
]

table_results = {}

for table_name in tables_to_test:
    try:
        print(f"\n📊 Testing table: {table_name}")
        
        # Test table existence and count
        response = supabase.table(table_name).select("*", count="exact").limit(1).execute()
        
        count = response.count if hasattr(response, 'count') else len(response.data)
        print(f"  ✅ Table exists: {count} records")
        print(f"  ✅ Response status: Success")
        
        # Show sample data structure if records exist
        if response.data and len(response.data) > 0:
            sample = response.data[0]
            print(f"  📝 Sample columns: {list(sample.keys())}")
        
        table_results[table_name] = {"status": "success", "count": count, "data": response.data}
        
    except Exception as e:
        print(f"  ❌ Error accessing {table_name}: {e}")
        table_results[table_name] = {"status": "error", "error": str(e)}

print("\n🧪 DATA OPERATIONS TEST:")

# Test basic CRUD operations
try:
    print("\n1️⃣ Testing SELECT operation...")
    tourists = supabase.table("tourists").select("*").limit(5).execute()
    print(f"✅ SELECT: Retrieved {len(tourists.data)} tourists")
    
    print("\n2️⃣ Testing INSERT operation (safe test)...")
    # Insert a test record
    test_tourist = {
        "name": "Test Database Connection",
        "contact": "+1234567890",
        "emergency_contact": "+1234567890",
        "safety_score": 100,
        "is_active": True,
        "nationality": "Test"
    }
    
    insert_result = supabase.table("tourists").insert(test_tourist).execute()
    if insert_result.data:
        test_id = insert_result.data[0]["id"]
        print(f"✅ INSERT: Created test record with ID {test_id}")
        
        print("\n3️⃣ Testing UPDATE operation...")
        update_result = supabase.table("tourists").update({
            "name": "Test Database Connection - Updated"
        }).eq("id", test_id).execute()
        print(f"✅ UPDATE: Modified test record")
        
        print("\n4️⃣ Testing DELETE operation...")
        delete_result = supabase.table("tourists").delete().eq("id", test_id).execute()
        print(f"✅ DELETE: Removed test record")
        
    else:
        print("⚠️ INSERT: Failed to create test record")

except Exception as e:
    print(f"❌ CRUD operations failed: {e}")
    traceback.print_exc()

print("\n⚡ REAL-TIME DATA TEST:")

try:
    # Get recent data
    recent_locations = supabase.table("locations").select("*").order("created_at", desc=True).limit(10).execute()
    recent_alerts = supabase.table("alerts").select("*").order("timestamp", desc=True).limit(10).execute()
    
    print(f"✅ Recent locations: {len(recent_locations.data)}")
    print(f"✅ Recent alerts: {len(recent_alerts.data)}")
    
    # Test time-based queries
    one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
    recent_data = supabase.table("locations").select("*").gte("created_at", one_hour_ago).execute()
    print(f"✅ Data from last hour: {len(recent_data.data)} locations")
    
except Exception as e:
    print(f"❌ Real-time data test failed: {e}")

print("\n🎯 FINAL ANALYSIS:")
print("-" * 40)

# Summary
success_count = sum(1 for result in table_results.values() if result.get("status") == "success")
total_tables = len(table_results)

print(f"📊 Table Access: {success_count}/{total_tables} successful")
print(f"🔗 Connection Status: {'✅ HEALTHY' if success_count > 0 else '❌ FAILED'}")
print(f"🗃️ Total Records Found: {sum(result.get('count', 0) for result in table_results.values() if result.get('status') == 'success')}")

# Detailed table status
print("\n📋 Table-by-Table Status:")
for table, result in table_results.items():
    status_icon = "✅" if result.get("status") == "success" else "❌"
    count = result.get("count", 0)
    print(f"  {status_icon} {table}: {count} records")

print(f"\n🕐 Analysis completed at: {datetime.now().isoformat()}")

if success_count == total_tables:
    print("\n🎉 RESULT: Database connection is FULLY FUNCTIONAL!")
else:
    print("\n⚠️ RESULT: Some database issues detected. Check errors above.")