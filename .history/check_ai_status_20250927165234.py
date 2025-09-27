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
        
    # Check AI status
    response = requests.get('http://localhost:8000/api/v1/ai/status', timeout=5)
    if response.status_code == 200:
        ai_status = response.json()
        print(f'🧠 AI Status: {ai_status["status"]}')
        print(f'🔧 Models: {ai_status.get("models_loaded", [])}')
    else:
        print('⚠️ AI Engine not initialized yet')
        
    # Check training status
    response = requests.get('http://localhost:8000/api/v1/ai/training/status', timeout=5)
    if response.status_code == 200:
        training = response.json()
        interval = training['global_settings']['retrain_interval_seconds']
        print(f'⏰ Training Interval: {interval} seconds ({interval/60:.1f} minutes)')
        
        for model, status in training['training_status'].items():
            next_training = status['next_training_in_seconds']
            print(f'🤖 {model}: Next training in {next_training}s')
    else:
        print('⚠️ Training status not available')
        
except requests.exceptions.ConnectionError:
    print('❌ Cannot connect to server. Is it running?')
    print('💡 Start with: python main.py')
except Exception as e:
    print(f'💥 Error: {e}')

print()
print('🚀 To start monitoring: python ai_status_dashboard.py')
print('🧪 To test training: python test_ai_training.py')