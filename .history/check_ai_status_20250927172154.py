#!/usr/bin/env python3
"""
🔍 Quick AI Engine Status Check
"""

import requests
import json
from datetime import datetime

print('🤖 Checking AI Engine Status...')
print('=' * 40)

try:
    # Check if server is running - try both endpoints
    health_endpoints = ['/health', '/']
    health_data = None
    
    for endpoint in health_endpoints:
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f'✅ Server Status: {health_data["status"]}')
                print(f'💾 Database: {health_data["database"]}')
                print(f'📍 Health endpoint: {endpoint}')
                break
        except:
            continue
    
    if not health_data:
        print('❌ Server not responding on any health endpoint')
        print('💡 Make sure server is running with: uvicorn main:app --host 0.0.0.0 --port 8000')
        print('🔧 Or use the new app structure: uvicorn app.main:app --host 0.0.0.0 --port 8000')
        exit(1)
        
    # Check AI status - use new endpoints
    response = requests.get('http://localhost:8000/ai/training/status', timeout=5)
    if response.status_code == 200:
        training_status = response.json()
        print(f'🧠 AI Training: {"🟢 Active" if training_status.get("training_count", 0) > 0 else "🟡 Initializing"}')
        print(f'📊 Training Count: {training_status.get("training_count", 0)}')
        print(f'⏰ Training Interval: {training_status.get("training_interval", "unknown")}')
        
        models = training_status.get("models_trained", [])
        if models:
            print(f'🤖 Models Trained: {", ".join(models)}')
        
        if training_status.get("last_training"):
            last_training = datetime.fromisoformat(training_status["last_training"])
            print(f'🕐 Last Training: {last_training.strftime("%H:%M:%S")}')
        
        if training_status.get("next_training"):
            next_training = datetime.fromisoformat(training_status["next_training"])
            print(f'⏰ Next Training: {next_training.strftime("%H:%M:%S")}')
    else:
        print('⚠️ AI Training status not available')
        
    # Check data stats
    response = requests.get('http://localhost:8000/ai/data/stats', timeout=5)
    if response.status_code == 200:
        data_stats = response.json()
        print(f'📈 Data Stats:')
        print(f'   Locations: {data_stats.get("total_locations", 0)}')
        print(f'   Tourists: {data_stats.get("total_tourists", 0)}')
        print(f'   Alerts: {data_stats.get("total_alerts", 0)}')
        print(f'   Recent Activity (1h): {data_stats.get("recent_locations_1h", 0)} locations, {data_stats.get("recent_alerts_1h", 0)} alerts')
    else:
        print('⚠️ Data statistics not available')
        
except requests.exceptions.ConnectionError:
    print('❌ Cannot connect to server. Is it running?')
    print('💡 Start with: python main.py')
except Exception as e:
    print(f'💥 Error: {e}')

print()
print('🚀 To start monitoring: python ai_status_dashboard.py')
print('🧪 To test training: python test_ai_training.py')