#!/usr/bin/env python3
"""
🖥️ AI Training Status Dashboard
Real-time display of AI training activity every 1 minute
"""

import requests
import json
import time
import os
from datetime import datetime


class AIStatusDashboard:
    """Real-time AI status dashboard."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_status(self):
        """Display current AI status."""
        try:
            # Get AI status
            response = requests.get(f"{self.base_url}/api/v1/ai/status")
            if response.status_code != 200:
                print("❌ Failed to get AI status")
                return False
            
            ai_status = response.json()
            
            # Get training status
            response = requests.get(f"{self.base_url}/api/v1/ai/training/status")
            if response.status_code != 200:
                print("❌ Failed to get training status")
                return False
            
            training_status = response.json()
            
            # Get data statistics
            response = requests.get(f"{self.base_url}/api/v1/ai/data/stats")
            data_stats = response.json() if response.status_code == 200 else {}
            
            # Clear screen and display dashboard
            self.clear_screen()
            
            print("🤖 SMART TOURIST SAFETY - AI TRAINING DASHBOARD")
            print("=" * 60)
            print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🌐 API Status: {ai_status.get('status', 'unknown')}")
            print(f"🔄 Training Interval: {training_status['global_settings']['retrain_interval_seconds']} seconds")
            print()
            
            # Model Status
            print("🧠 MODEL STATUS:")
            print("-" * 30)
            for model_type, status in training_status['training_status'].items():
                next_training = status['next_training_in_seconds']
                last_trained = status['last_trained']
                
                if status['is_due_for_training']:
                    status_icon = "🔥"
                    status_text = "TRAINING DUE!"
                elif next_training <= 30:
                    status_icon = "⚠️"
                    status_text = f"Training in {next_training}s"
                else:
                    status_icon = "✅"
                    status_text = f"Next: {next_training}s"
                
                print(f"{status_icon} {model_type.replace('_', ' ').title()}:")
                print(f"   Last trained: {last_trained}")
                print(f"   Status: {status_text}")
                print()
            
            # Data Statistics
            if data_stats:
                print("📊 DATA STATISTICS:")
                print("-" * 30)
                locations = data_stats.get('database_stats', {}).get('locations', {})
                
                if 'last_hour' in locations:
                    print(f"📍 Locations (last hour): {locations['last_hour']['location_updates']}")
                    print(f"👥 Active tourists: {data_stats['summary']['active_tourists']}")
                    print(f"💾 Data availability: {data_stats['summary']['training_data_availability']}")
                print()
            
            # Performance Metrics
            performance = ai_status.get('performance_metrics', {})
            if performance:
                print("📈 PERFORMANCE METRICS:")
                print("-" * 30)
                for model_type, metrics in performance.items():
                    if isinstance(metrics, dict):
                        training_samples = metrics.get('training_samples', 'N/A')
                        training_time = metrics.get('training_time', 'N/A')
                        print(f"🎯 {model_type.replace('_', ' ').title()}:")
                        print(f"   Training samples: {training_samples}")
                        print(f"   Last training: {training_time}")
                print()
            
            # Activity Log
            print("🔄 ACTIVITY LOG:")
            print("-" * 30)
            print("✅ Real-time processing: Every 15 seconds")
            print("🔄 Model retraining: Every 60 seconds")
            print("📊 Data fetching: Continuous")
            print("🚨 Alert generation: Real-time")
            
            print("\n" + "=" * 60)
            print("Press Ctrl+C to stop monitoring...")
            
            return True
            
        except Exception as e:
            print(f"💥 Error displaying status: {e}")
            return False
    
    def run_dashboard(self, refresh_interval=10):
        """Run the real-time dashboard."""
        print("🚀 Starting AI Training Status Dashboard...")
        print(f"🔄 Refreshing every {refresh_interval} seconds...")
        
        try:
            while True:
                success = self.display_status()
                if not success:
                    print("⚠️ Dashboard error, retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    time.sleep(refresh_interval)
                    
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped by user")
        except Exception as e:
            print(f"\n💥 Dashboard crashed: {e}")


def main():
    """Main function."""
    dashboard = AIStatusDashboard()
    dashboard.run_dashboard(refresh_interval=10)  # Refresh every 10 seconds


if __name__ == "__main__":
    main()