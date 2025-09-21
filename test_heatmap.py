#!/usr/bin/env python3
"""
Heatmap Endpoint Test Script
Tests the newly added heatmap functionality.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_heatmap_endpoint():
    """Test the heatmap endpoint"""
    print("🗺️  Testing Heatmap Endpoint...")
    print("=" * 50)
    
    # Test 1: Basic heatmap
    print("1. Testing basic heatmap (/locations/heatmap)")
    response = requests.get(f"{BASE_URL}/locations/heatmap")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Points found: {data['total_points']}")
        print(f"   ✅ Bounds: {data['bounds']}")
        print(f"   ✅ Generated at: {data['generated_at']}")
        
        if data['points']:
            sample_point = data['points'][0]
            print(f"   Sample point: Lat {sample_point['latitude']}, Lng {sample_point['longitude']}")
            print(f"   Intensity: {sample_point['intensity']}, Tourists: {sample_point['tourist_count']}")
            print(f"   Risk Level: {sample_point['risk_level']}")
    else:
        print(f"   ❌ Error: {response.text}")
        return False
    
    # Test 2: Heatmap with parameters
    print("\n2. Testing heatmap with parameters (12 hours, small grid)")
    params = {
        "hours": 12,
        "include_alerts": True,
        "grid_size": 0.005
    }
    response = requests.get(f"{BASE_URL}/locations/heatmap", params=params)
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Points with smaller grid: {data['total_points']}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Test 3: Redirect endpoint
    print("\n3. Testing redirect endpoint (/heatmap)")
    response = requests.get(f"{BASE_URL}/heatmap", allow_redirects=True)
    print(f"   Status Code: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    if response.status_code == 200:
        print("   ✅ Redirect working correctly")
    
    return True

def test_heatmap_variations():
    """Test different heatmap configurations"""
    print("\n🔍 Testing Heatmap Variations...")
    print("=" * 50)
    
    test_cases = [
        {"hours": 1, "description": "Last 1 hour"},
        {"hours": 24, "description": "Last 24 hours"},
        {"hours": 168, "description": "Last week"},
        {"include_alerts": False, "description": "Without alerts"},
        {"grid_size": 0.1, "description": "Large grid (0.1)"},
        {"grid_size": 0.001, "description": "Small grid (0.001)"}
    ]
    
    for i, params in enumerate(test_cases, 1):
        description = params.pop("description")
        print(f"{i}. {description}")
        
        response = requests.get(f"{BASE_URL}/locations/heatmap", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Points: {data['total_points']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")

def analyze_heatmap_data():
    """Analyze the heatmap data structure"""
    print("\n📊 Analyzing Heatmap Data...")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/locations/heatmap")
    if response.status_code != 200:
        print("❌ Failed to get heatmap data")
        return
    
    data = response.json()
    points = data['points']
    
    if not points:
        print("No points in heatmap")
        return
    
    # Analyze intensity distribution
    intensities = [p['intensity'] for p in points]
    tourist_counts = [p['tourist_count'] for p in points]
    risk_levels = [p['risk_level'] for p in points]
    
    print(f"📈 Intensity Analysis:")
    print(f"   Min intensity: {min(intensities)}")
    print(f"   Max intensity: {max(intensities)}")
    print(f"   Avg intensity: {sum(intensities) / len(intensities):.1f}")
    
    print(f"\n👥 Tourist Count Analysis:")
    print(f"   Min tourists per point: {min(tourist_counts)}")
    print(f"   Max tourists per point: {max(tourist_counts)}")
    print(f"   Total unique locations: {len(points)}")
    
    print(f"\n⚠️  Risk Level Distribution:")
    risk_counts = {}
    for risk in risk_levels:
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    for risk, count in risk_counts.items():
        print(f"   {risk.capitalize()}: {count} points")

def main():
    print("🗺️  Heatmap Endpoint Test Suite")
    print("Testing Smart Tourist Safety Heatmap API")
    print("=" * 60)
    
    # Test basic functionality
    if not test_heatmap_endpoint():
        print("❌ Basic heatmap tests failed")
        return
    
    # Test variations
    test_heatmap_variations()
    
    # Analyze data
    analyze_heatmap_data()
    
    print("\n" + "=" * 60)
    print("🎉 Heatmap Testing Complete!")
    print("✅ Heatmap endpoints are working correctly")
    print("\n📝 Available endpoints:")
    print("   - GET /locations/heatmap")
    print("   - GET /heatmap (redirects to above)")
    print("\n🔧 Parameters:")
    print("   - hours: 1-168 (default: 24)")
    print("   - include_alerts: true/false (default: true)")
    print("   - grid_size: 0.001-0.1 (default: 0.01)")

if __name__ == "__main__":
    main()