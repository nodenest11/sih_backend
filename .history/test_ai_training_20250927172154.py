#!/usr/bin/env python3
"""
🧪 AI Training Test Script
Tests the 1-minute AI training functionality
"""

import asyncio
import requests
import json
import time
from datetime import datetime


class AITrainingTester:
    """Test the AI training every 1 minute functionality."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    async def test_ai_training_schedule(self):
        """Test the AI training schedule and monitoring."""
        print("🧪 Testing AI Training Every 1 Minute")
        print("=" * 50)
        
        try:
            # 1. Check AI Engine Status
            print("1️⃣ Checking AI Engine Status...")
            response = requests.get(f"{self.base_url}/api/v1/ai/status")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ AI Engine Status: {status['status']}")
                print(f"📊 Models loaded: {status.get('models_loaded', [])}")
                print(f"⏰ Last training times: {status.get('last_training_times', {})}")
            else:
                print(f"❌ Failed to get AI status: {response.status_code}")
                return
            
            # 2. Check Training Status
            print("\n2️⃣ Checking Training Status...")
            response = requests.get(f"{self.base_url}/api/v1/ai/training/status")
            if response.status_code == 200:
                training_status = response.json()
                print(f"🔄 Training interval: {training_status['global_settings']['retrain_interval_seconds']} seconds")
                
                for model_type, status in training_status['training_status'].items():
                    print(f"🤖 {model_type}:")
                    print(f"   Last trained: {status['last_trained']}")
                    print(f"   Next training in: {status['next_training_in_seconds']} seconds")
                    print(f"   Due for training: {status['is_due_for_training']}")
            else:
                print(f"❌ Failed to get training status: {response.status_code}")
            
            # 3. Check Data Statistics
            print("\n3️⃣ Checking Data Statistics...")
            response = requests.get(f"{self.base_url}/api/v1/ai/data/stats")
            if response.status_code == 200:
                data_stats = response.json()
                locations = data_stats['database_stats']['locations']
                print(f"📍 Locations (last hour): {locations['last_hour']['location_updates']}")
                print(f"👥 Active tourists: {data_stats['summary']['active_tourists']}")
                print(f"💾 Data availability: {data_stats['summary']['training_data_availability']}")
            else:
                print(f"❌ Failed to get data statistics: {response.status_code}")
            
            # 4. Force Training Test
            print("\n4️⃣ Testing Force Training...")
            response = requests.post(f"{self.base_url}/api/v1/ai/retrain/force_all")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Force training initiated: {result['message']}")
                print(f"🕒 Timestamp: {result['timestamp']}")
            else:
                print(f"❌ Failed to force training: {response.status_code}")
            
            # 5. Monitor Training for 3 minutes
            print("\n5️⃣ Monitoring Training Activity (next 3 minutes)...")
            print("⏰ Watching for training activity every 30 seconds...")
            
            for i in range(6):  # 6 * 30 seconds = 3 minutes
                print(f"\n🔍 Check #{i+1} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Get current training status
                response = requests.get(f"{self.base_url}/api/v1/ai/training/status")
                if response.status_code == 200:
                    training_status = response.json()
                    
                    for model_type, status in training_status['training_status'].items():
                        next_training = status['next_training_in_seconds']
                        if next_training <= 30:  # Training due soon
                            print(f"🔥 {model_type} training due in {next_training}s!")
                        elif status['is_due_for_training']:
                            print(f"⚠️ {model_type} training overdue!")
                        else:
                            print(f"✅ {model_type} next training in {next_training}s")
                
                # Wait 30 seconds before next check
                if i < 5:  # Don't sleep after the last iteration
                    await asyncio.sleep(30)
            
            print("\n6️⃣ Final Status Check...")
            response = requests.get(f"{self.base_url}/api/v1/ai/status")
            if response.status_code == 200:
                final_status = response.json()
                print(f"🏁 Final models loaded: {final_status.get('models_loaded', [])}")
                print(f"📈 Performance metrics available: {bool(final_status.get('performance_metrics', {}))}")
            
            print("\n🎉 AI Training Test Completed!")
            
        except Exception as e:
            print(f"💥 Test failed with error: {e}")
    
    def test_manual_training_trigger(self):
        """Test manual training triggers."""
        print("\n🔧 Testing Manual Training Triggers...")
        
        triggers = ['isolation_forest', 'temporal_autoencoder', 'all', 'force_all']
        
        for trigger in triggers:
            print(f"🚀 Triggering {trigger} training...")
            response = requests.post(f"{self.base_url}/api/v1/ai/retrain/{trigger}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {trigger}: {result['message']}")
            else:
                print(f"❌ {trigger} failed: {response.status_code}")
            
            time.sleep(2)  # Wait between triggers
    
    def generate_test_data(self):
        """Generate some test data for training."""
        print("\n📊 Generating Test Data...")
        
        # Register a test tourist
        tourist_data = {
            "name": "AI Test User",
            "contact": "+91-9999999999",
            "emergency_contact": "+91-9999999998",
            "age": 25
        }
        
        response = requests.post(f"{self.base_url}/registerTourist", json=tourist_data)
        if response.status_code == 201:
            tourist_id = response.json()["id"]
            print(f"✅ Created test tourist: {tourist_id}")
            
            # Send several location updates
            locations = [
                (28.6139, 77.2090, 5.0),   # Delhi
                (28.6200, 77.2150, 10.0), # Moving
                (28.6300, 77.2200, 8.0),  # Moving
                (28.6350, 77.2250, 0.0),  # Stopped
                (28.6400, 77.2300, 15.0), # Fast movement
            ]
            
            for i, (lat, lon, speed) in enumerate(locations):
                location_data = {
                    "tourist_id": tourist_id,
                    "latitude": lat,
                    "longitude": lon,
                    "speed": speed
                }
                
                response = requests.post(f"{self.base_url}/sendLocation", json=location_data)
                if response.status_code == 201:
                    print(f"📍 Location update {i+1} sent successfully")
                else:
                    print(f"❌ Location update {i+1} failed")
                
                time.sleep(1)  # Space out the updates
            
            return tourist_id
        else:
            print(f"❌ Failed to create test tourist: {response.status_code}")
            return None


async def main():
    """Main test function."""
    tester = AITrainingTester()
    
    print("🎯 Smart Tourist Safety - AI Training Test")
    print("=" * 60)
    
    # Generate test data first
    tourist_id = tester.generate_test_data()
    
    if tourist_id:
        print(f"\n✅ Test data generated with tourist ID: {tourist_id}")
    else:
        print("\n⚠️ Continuing without test data...")
    
    # Test manual triggers
    tester.test_manual_training_trigger()
    
    # Test the main training schedule
    await tester.test_ai_training_schedule()


if __name__ == "__main__":
    asyncio.run(main())