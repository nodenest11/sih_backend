#!/usr/bin/env python3
"""
🎯 Real-time AI Training Monitor
Watch the 1-minute training cycles in action!
"""

import requests
import time
from datetime import datetime
import json

def get_training_status():
    """Get current training status"""
    try:
        response = requests.get('http://localhost:8000/ai/training/status', timeout=3)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def print_status(status, clear_screen=True):
    """Print formatted training status"""
    if clear_screen:
        print('\033[2J\033[H', end='')  # Clear screen and move cursor to top
    
    print("🤖 AI Training Monitor - Live Status")
    print("=" * 50)
    print(f"⏰ Current Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    if status:
        training_state = "🔄 TRAINING" if status['is_training'] else "⏸️ WAITING"
        print(f"📊 Status: {training_state}")
        print(f"🔢 Training Cycles Completed: {status['training_count']}")
        print(f"⚡ Training Interval: {status['training_interval']}")
        print()
        
        if status['last_training']:
            last_time = datetime.fromisoformat(status['last_training'])
            print(f"🕐 Last Training: {last_time.strftime('%H:%M:%S')}")
        
        if status['next_training']:
            next_time = datetime.fromisoformat(status['next_training'])
            time_diff = (next_time - datetime.now()).total_seconds()
            print(f"⏰ Next Training: {next_time.strftime('%H:%M:%S')} (in {time_diff:.0f}s)")
        
        print()
        models = status.get('models_trained', [])
        print(f"🧠 Models Trained: {len(models)}")
        for model in models:
            print(f"   • {model}")
        
        print()
        print("💡 Press Ctrl+C to exit")
        
    else:
        print("❌ Cannot connect to AI engine")
        print("💡 Make sure server is running on localhost:8000")

def main():
    """Main monitoring loop"""
    print("🚀 Starting AI Training Monitor...")
    print("📡 Connecting to AI engine...")
    
    last_training_count = 0
    
    try:
        while True:
            status = get_training_status()
            
            if status:
                current_count = status.get('training_count', 0)
                
                # Check if new training cycle completed
                if current_count > last_training_count:
                    print(f"\n🎉 NEW TRAINING CYCLE COMPLETED! (#{current_count})")
                    last_training_count = current_count
                
                print_status(status)
            else:
                print_status(None, clear_screen=False)
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped. AI engine continues running in background!")
        print("🔗 Check status anytime with: python check_ai_status.py")

if __name__ == "__main__":
    main()