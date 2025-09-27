"""
🔍 Database Connectivity Test
Clean test to verify Supabase connection and table structure
"""

import os
import logging
from supabase import create_client, Client
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_connectivity():
    """Test Supabase database connectivity and table access"""
    
    # Load environment variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        logger.error("❌ Missing Supabase credentials")
        return False
    
    try:
        # Initialize client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("✅ Supabase client created successfully")
        
        # Test each table
        tables_to_test = [
            "tourists", "locations", "alerts", "ai_assessments", 
            "safe_zones", "restricted_zones"
        ]
        
        table_results = {}
        
        for table_name in tables_to_test:
            try:
                # Test table access with count
                result = supabase.table(table_name).select("*", count="exact").limit(1).execute()
                count = result.count if hasattr(result, 'count') else len(result.data)
                table_results[table_name] = {"status": "✅", "count": count}
                logger.info(f"✅ {table_name}: {count} records")
                
            except Exception as e:
                table_results[table_name] = {"status": "❌", "error": str(e)}
                logger.error(f"❌ {table_name}: {e}")
        
        # Summary
        successful_tables = sum(1 for r in table_results.values() if r["status"] == "✅")
        total_tables = len(tables_to_test)
        
        logger.info(f"\n📊 DATABASE CONNECTIVITY SUMMARY:")
        logger.info(f"✅ Connected Tables: {successful_tables}/{total_tables}")
        logger.info(f"📡 Connection URL: {SUPABASE_URL}")
        logger.info(f"🔑 Authentication: {'✅ Valid' if successful_tables > 0 else '❌ Invalid'}")
        
        if successful_tables == total_tables:
            logger.info("🎉 ALL DATABASE CONNECTIONS SUCCESSFUL!")
            return True
        else:
            logger.warning(f"⚠️  {total_tables - successful_tables} tables have connectivity issues")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Database Connectivity Test...")
    success = test_database_connectivity()
    
    if success:
        logger.info("✅ Database connectivity test PASSED")
    else:
        logger.error("❌ Database connectivity test FAILED")