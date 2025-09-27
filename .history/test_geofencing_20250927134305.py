"""
🗺️ Geofencing Verification Test
Test safe and restricted zone detection accuracy
"""

import os
import logging
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def check_geofence_detailed(latitude: float, longitude: float) -> dict:
    """Enhanced geofence checking with detailed logging"""
    
    logger.info(f"🔍 Checking geofence for coordinates: ({latitude}, {longitude})")
    
    try:
        # Check restricted zones
        logger.info("   📍 Checking restricted zones...")
        restricted_response = supabase.table("restricted_zones").select("*").eq("is_active", True).execute()
        logger.info(f"   Found {len(restricted_response.data)} active restricted zones")
        
        for i, zone in enumerate(restricted_response.data):
            logger.info(f"   Zone {i+1}: {zone['name']} ({zone['zone_type']})")
            coords = zone.get("coordinates", {}).get("coordinates", [[]])
            
            if coords and len(coords) > 0 and len(coords[0]) > 0:
                # Simple bounding box check
                lats = [point[1] for point in coords[0]]
                lons = [point[0] for point in coords[0]]
                
                min_lat, max_lat = min(lats), max(lats)
                min_lon, max_lon = min(lons), max(lons)
                
                logger.info(f"      Bounds: lat({min_lat:.4f} to {max_lat:.4f}), lon({min_lon:.4f} to {max_lon:.4f})")
                
                if (min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon):
                    logger.warning(f"   ⚠️  MATCH: Point is in restricted zone '{zone['name']}'")
                    return {
                        "status": "RESTRICTED",
                        "in_restricted_zone": True,
                        "zone_name": zone["name"],
                        "zone_type": zone["zone_type"],
                        "danger_level": zone["danger_level"],
                        "geofence_alert": True
                    }
                else:
                    logger.info(f"      ✅ Not in this restricted zone")
        
        # Check safe zones
        logger.info("   🏛️ Checking safe zones...")
        safe_response = supabase.table("safe_zones").select("*").eq("is_active", True).execute()
        logger.info(f"   Found {len(safe_response.data)} active safe zones")
        
        for i, zone in enumerate(safe_response.data):
            logger.info(f"   Zone {i+1}: {zone['name']} ({zone['zone_type']})")
            coords = zone.get("coordinates", {}).get("coordinates", [[]])
            
            if coords and len(coords) > 0 and len(coords[0]) > 0:
                lats = [point[1] for point in coords[0]]
                lons = [point[0] for point in coords[0]]
                
                min_lat, max_lat = min(lats), max(lats)
                min_lon, max_lon = min(lons), max(lons)
                
                logger.info(f"      Bounds: lat({min_lat:.4f} to {max_lat:.4f}), lon({min_lon:.4f} to {max_lon:.4f})")
                
                if (min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon):
                    logger.info(f"   ✅ MATCH: Point is in safe zone '{zone['name']}'")
                    return {
                        "status": "SAFE",
                        "in_safe_zone": True,
                        "zone_name": zone["name"],
                        "zone_type": zone["zone_type"],
                        "safety_rating": zone["safety_rating"],
                        "geofence_alert": False
                    }
                else:
                    logger.info(f"      ❓ Not in this safe zone")
        
        # Unknown area
        logger.info("   ❓ Point is in unknown area")
        return {
            "status": "UNKNOWN",
            "in_unknown_area": True,
            "geofence_alert": False
        }
        
    except Exception as e:
        logger.error(f"❌ Geofence check error: {e}")
        return {"status": "ERROR", "geofence_alert": False, "error": str(e)}

def test_geofencing():
    """Test geofencing with specific coordinates"""
    
    logger.info("🗺️ Starting Geofencing Verification Test")
    logger.info("=" * 60)
    
    # Test coordinates based on our database zones
    test_points = [
        {
            "name": "India Gate (Should be SAFE)",
            "lat": 28.6129,
            "lon": 77.2295,
            "expected": "SAFE"
        },
        {
            "name": "Red Fort Area (Should be SAFE)", 
            "lat": 28.6562,
            "lon": 77.2410,
            "expected": "SAFE"
        },
        {
            "name": "Military Area (Should be RESTRICTED)",
            "lat": 28.654,
            "lon": 77.241,
            "expected": "RESTRICTED"
        },
        {
            "name": "Industrial Zone (Should be RESTRICTED)",
            "lat": 28.655,
            "lon": 77.243,
            "expected": "RESTRICTED"  
        },
        {
            "name": "Random Location (Should be UNKNOWN)",
            "lat": 28.7000,
            "lon": 77.3000,
            "expected": "UNKNOWN"
        }
    ]
    
    results = []
    
    for point in test_points:
        logger.info(f"\n🧪 Testing: {point['name']}")
        logger.info(f"   Coordinates: ({point['lat']}, {point['lon']})")
        logger.info(f"   Expected: {point['expected']}")
        
        result = check_geofence_detailed(point["lat"], point["lon"])
        actual_status = result["status"]
        
        # Test result
        if actual_status == point["expected"]:
            logger.info(f"   ✅ PASS: Got {actual_status} as expected")
            test_passed = True
        else:
            logger.warning(f"   ❌ FAIL: Expected {point['expected']}, got {actual_status}")
            test_passed = False
        
        results.append({
            "point": point["name"],
            "expected": point["expected"],
            "actual": actual_status,
            "passed": test_passed,
            "details": result
        })
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 GEOFENCING TEST SUMMARY")
    logger.info("=" * 60)
    
    passed_tests = sum(1 for r in results if r["passed"])
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100
    
    logger.info(f"✅ Passed Tests: {passed_tests}/{total_tests}")
    logger.info(f"❌ Failed Tests: {total_tests - passed_tests}/{total_tests}")  
    logger.info(f"📈 Success Rate: {success_rate:.1f}%")
    
    # Detailed results
    logger.info(f"\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result["passed"] else "❌"
        logger.info(f"   {status_icon} {result['point']}")
        logger.info(f"      Expected: {result['expected']}, Got: {result['actual']}")
        if result["details"].get("zone_name"):
            logger.info(f"      Zone: {result['details']['zone_name']}")
    
    if success_rate >= 80:
        logger.info(f"\n🎉 GEOFENCING TEST PASSED! ({success_rate:.1f}% accuracy)")
        return True
    else:
        logger.warning(f"\n⚠️  GEOFENCING TEST NEEDS IMPROVEMENT ({success_rate:.1f}% accuracy)")
        return False

if __name__ == "__main__":
    success = test_geofencing()
    if success:
        logger.info("✅ Geofencing verification completed successfully")
    else:
        logger.error("❌ Geofencing verification failed")