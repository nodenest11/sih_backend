"""
🤖 AI System Verification Test
Test pattern recognition, anomaly detection, and AI reasoning
"""

import requests
import json
import logging
from datetime import datetime
import time
import random

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
TIMEOUT = 15

class AISystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.tourist_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if details:
            logger.info(f"   📋 {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def setup_test_tourist(self):
        """Create test tourist for AI testing"""
        tourist_data = {
            "name": "AI Test Tourist",
            "contact": f"+91-{int(time.time()) % 10000000000}",
            "email": f"aitest{int(time.time())}@example.com",
            "emergency_contact": "+91-9876543210",
            "age": 30,
            "nationality": "Indian"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/registerTourist", 
                                       json=tourist_data, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                self.tourist_id = data.get('tourist_id')
                logger.info(f"✅ Created test tourist ID: {self.tourist_id}")
                return True
            else:
                logger.error("❌ Failed to create test tourist")
                return False
        except Exception as e:
            logger.error(f"❌ Tourist setup error: {e}")
            return False
    
    def test_normal_behavior_detection(self):
        """Test AI's ability to detect normal tourist behavior"""
        logger.info("🧠 Testing Normal Behavior Detection...")
        
        # Simulate normal tourist walking pattern
        normal_locations = [
            {"lat": 28.6129, "lon": 77.2295, "speed": 2.5, "desc": "Walking at India Gate"},
            {"lat": 28.6135, "lon": 77.2300, "speed": 3.0, "desc": "Slow walking"},
            {"lat": 28.6140, "lon": 77.2305, "speed": 2.8, "desc": "Normal pace"},
            {"lat": 28.6145, "lon": 77.2310, "speed": 2.0, "desc": "Stopping to look"},
        ]
        
        assessments = []
        for i, loc in enumerate(normal_locations):
            location_data = {
                "tourist_id": self.tourist_id,
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "speed": loc["speed"]
            }
            
            try:
                response = self.session.post(f"{BASE_URL}/sendLocation", 
                                           json=location_data, timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    assessment = data.get('assessment', {})
                    assessments.append(assessment)
                    
                    logger.info(f"   {loc['desc']}: Safety={assessment.get('safety_score')}, "
                              f"Severity={assessment.get('severity')}, "
                              f"Anomaly={assessment.get('anomaly_score')}")
                    time.sleep(0.5)
                else:
                    logger.error(f"   Failed to send location {i+1}")
                    return False
            except Exception as e:
                logger.error(f"   Location update error: {e}")
                return False
        
        # Analyze AI response to normal behavior
        if assessments:
            avg_safety = sum(a.get('safety_score', 0) for a in assessments) / len(assessments)
            safe_count = sum(1 for a in assessments if a.get('severity') == 'SAFE')
            avg_anomaly = sum(a.get('anomaly_score', 0) for a in assessments) / len(assessments)
            
            # AI should recognize this as normal behavior
            if avg_safety >= 80 and safe_count >= 3 and avg_anomaly <= 0.3:
                self.log_test("Normal Behavior Detection", True,
                             f"AI correctly identified normal behavior: Safety={avg_safety:.1f}, "
                             f"Safe assessments: {safe_count}/4, Avg Anomaly: {avg_anomaly:.2f}")
                return True
            else:
                self.log_test("Normal Behavior Detection", False,
                             f"AI failed normal behavior: Safety={avg_safety:.1f}, "
                             f"Anomaly={avg_anomaly:.2f}")
                return False
        
        return False
    
    def test_speed_anomaly_detection(self):
        """Test AI's speed anomaly detection capabilities"""
        logger.info("🚗 Testing Speed Anomaly Detection...")
        
        speed_scenarios = [
            {"speed": 5.0, "desc": "Normal walking", "expected": "SAFE"},
            {"speed": 25.0, "desc": "Cycling speed", "expected": "SAFE"},
            {"speed": 50.0, "desc": "Moderate vehicle", "expected": "WARNING"},
            {"speed": 85.0, "desc": "High speed vehicle", "expected": "CRITICAL"},
            {"speed": 0.0, "desc": "Stationary", "expected": "SAFE"}
        ]
        
        correct_detections = 0
        for scenario in speed_scenarios:
            location_data = {
                "tourist_id": self.tourist_id,
                "latitude": 28.6129,
                "longitude": 77.2295,
                "speed": scenario["speed"]
            }
            
            try:
                response = self.session.post(f"{BASE_URL}/sendLocation", 
                                           json=location_data, timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    assessment = data.get('assessment', {})
                    severity = assessment.get('severity')
                    anomaly_score = assessment.get('anomaly_score', 0)
                    
                    logger.info(f"   {scenario['desc']} ({scenario['speed']} km/h): "
                              f"Severity={severity}, Anomaly={anomaly_score:.2f}")
                    
                    # Check if AI response matches expectations
                    if scenario["expected"] == "CRITICAL" and severity == "CRITICAL":
                        correct_detections += 1
                    elif scenario["expected"] == "WARNING" and severity in ["WARNING", "CRITICAL"]:
                        correct_detections += 1
                    elif scenario["expected"] == "SAFE" and severity == "SAFE":
                        correct_detections += 1
                    
                    time.sleep(0.5)
                else:
                    logger.error(f"   Failed speed test: {scenario['desc']}")
            except Exception as e:
                logger.error(f"   Speed test error: {e}")
        
        accuracy = correct_detections / len(speed_scenarios)
        if accuracy >= 0.6:  # 60% accuracy threshold
            self.log_test("Speed Anomaly Detection", True,
                         f"Detected {correct_detections}/{len(speed_scenarios)} scenarios correctly "
                         f"({accuracy*100:.0f}% accuracy)")
            return True
        else:
            self.log_test("Speed Anomaly Detection", False,
                         f"Only {correct_detections}/{len(speed_scenarios)} correct "
                         f"({accuracy*100:.0f}% accuracy)")
            return False
    
    def test_geofence_intelligence(self):
        """Test AI geofencing intelligence"""
        logger.info("🗺️ Testing Geofence Intelligence...")
        
        zone_tests = [
            {"lat": 28.6129, "lon": 77.2295, "desc": "Safe zone (India Gate)", 
             "expected_safe": True, "expected_alert": False},
            {"lat": 28.654, "lon": 77.241, "desc": "Restricted zone (Military)", 
             "expected_safe": False, "expected_alert": True},
            {"lat": 28.7000, "lon": 77.3000, "desc": "Unknown area", 
             "expected_safe": False, "expected_alert": False},
        ]
        
        correct_assessments = 0
        for test in zone_tests:
            location_data = {
                "tourist_id": self.tourist_id,
                "latitude": test["lat"],
                "longitude": test["lon"],
                "speed": 3.0
            }
            
            try:
                response = self.session.post(f"{BASE_URL}/sendLocation", 
                                           json=location_data, timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    assessment = data.get('assessment', {})
                    severity = assessment.get('severity')
                    geofence_alert = assessment.get('geofence_alert', False)
                    safety_score = assessment.get('safety_score', 0)
                    
                    logger.info(f"   {test['desc']}: Severity={severity}, "
                              f"Geofence Alert={geofence_alert}, Safety={safety_score}")
                    
                    # Validate AI geofence reasoning
                    if test["expected_safe"] and severity == "SAFE":
                        correct_assessments += 1
                    elif not test["expected_safe"] and severity in ["WARNING", "CRITICAL"]:
                        correct_assessments += 1
                    elif test["expected_alert"] == geofence_alert:
                        correct_assessments += 1
                    
                    time.sleep(0.5)
                else:
                    logger.error(f"   Failed geofence test: {test['desc']}")
            except Exception as e:
                logger.error(f"   Geofence test error: {e}")
        
        accuracy = correct_assessments / len(zone_tests)
        if accuracy >= 0.7:  # 70% accuracy
            self.log_test("Geofence Intelligence", True,
                         f"AI correctly assessed {correct_assessments}/{len(zone_tests)} zones "
                         f"({accuracy*100:.0f}% accuracy)")
            return True
        else:
            self.log_test("Geofence Intelligence", False,
                         f"AI only got {correct_assessments}/{len(zone_tests)} zones correct")
            return False
    
    def test_pattern_learning(self):
        """Test AI's ability to learn from patterns"""
        logger.info("📈 Testing Pattern Learning...")
        
        # Create a suspicious pattern: alternating between safe and risky behavior
        pattern_locations = [
            {"lat": 28.6129, "lon": 77.2295, "speed": 3.0, "desc": "Normal start"},
            {"lat": 28.6200, "lon": 77.2350, "speed": 75.0, "desc": "High speed"},
            {"lat": 28.6250, "lon": 77.2400, "speed": 2.0, "desc": "Suddenly slow"},
            {"lat": 28.654, "lon": 77.241, "speed": 5.0, "desc": "Enter restricted"},
            {"lat": 28.6129, "lon": 77.2295, "speed": 90.0, "desc": "High speed again"}
        ]
        
        safety_scores = []
        anomaly_scores = []
        
        for i, loc in enumerate(pattern_locations):
            location_data = {
                "tourist_id": self.tourist_id,
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "speed": loc["speed"]
            }
            
            try:
                response = self.session.post(f"{BASE_URL}/sendLocation", 
                                           json=location_data, timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    assessment = data.get('assessment', {})
                    safety_score = assessment.get('safety_score', 0)
                    anomaly_score = assessment.get('anomaly_score', 0)
                    
                    safety_scores.append(safety_score)
                    anomaly_scores.append(anomaly_score)
                    
                    logger.info(f"   Step {i+1} - {loc['desc']}: "
                              f"Safety={safety_score}, Anomaly={anomaly_score:.2f}")
                    
                    time.sleep(0.5)
                else:
                    logger.error(f"   Failed pattern step {i+1}")
                    return False
            except Exception as e:
                logger.error(f"   Pattern test error: {e}")
                return False
        
        # Analyze if AI learned the escalating risk pattern
        if len(safety_scores) >= 3:
            # Safety should generally decrease as risky behavior increases
            final_safety = safety_scores[-1]
            max_anomaly = max(anomaly_scores)
            
            if final_safety < 50 and max_anomaly > 0.5:
                self.log_test("Pattern Learning", True,
                             f"AI learned suspicious pattern: Final Safety={final_safety}, "
                             f"Max Anomaly={max_anomaly:.2f}")
                return True
            else:
                self.log_test("Pattern Learning", False,
                             f"AI didn't learn pattern well: Safety={final_safety}, "
                             f"Anomaly={max_anomaly:.2f}")
                return False
        
        return False
    
    def test_alert_generation_intelligence(self):
        """Test intelligent alert generation"""
        logger.info("🚨 Testing Alert Generation Intelligence...")
        
        # Get initial alert count
        initial_response = self.session.get(f"{BASE_URL}/getAlerts?tourist_id={self.tourist_id}")
        initial_count = 0
        if initial_response.status_code == 200:
            initial_count = len(initial_response.json().get('alerts', []))
        
        # Trigger various alert scenarios
        alert_scenarios = [
            {"lat": 28.654, "lon": 77.241, "speed": 0.0, "desc": "Stationary in restricted zone"},
            {"lat": 28.6129, "lon": 77.2295, "speed": 100.0, "desc": "Extreme speed in safe zone"},
            {"lat": 28.6200, "lon": 77.2350, "speed": 5.0, "desc": "Normal behavior (no alert expected)"}
        ]
        
        alerts_generated = 0
        for scenario in alert_scenarios:
            location_data = {
                "tourist_id": self.tourist_id,
                "latitude": scenario["lat"],
                "longitude": scenario["lon"],
                "speed": scenario["speed"]
            }
            
            try:
                response = self.session.post(f"{BASE_URL}/sendLocation", 
                                           json=location_data, timeout=TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    alert_generated = data.get('alert_generated', False)
                    assessment = data.get('assessment', {})
                    
                    logger.info(f"   {scenario['desc']}: Alert Generated={alert_generated}, "
                              f"Severity={assessment.get('severity')}")
                    
                    if alert_generated and "Normal behavior" not in scenario["desc"]:
                        alerts_generated += 1
                    elif not alert_generated and "Normal behavior" in scenario["desc"]:
                        alerts_generated += 0.5  # Partial credit for not generating false alert
                    
                    time.sleep(1)
                else:
                    logger.error(f"   Failed alert test: {scenario['desc']}")
            except Exception as e:
                logger.error(f"   Alert test error: {e}")
        
        # Check final alert count
        final_response = self.session.get(f"{BASE_URL}/getAlerts?tourist_id={self.tourist_id}")
        final_count = 0
        if final_response.status_code == 200:
            final_count = len(final_response.json().get('alerts', []))
        
        new_alerts = final_count - initial_count
        
        if new_alerts >= 1 and alerts_generated >= 1.5:  # At least one real alert + no false positives
            self.log_test("Alert Generation Intelligence", True,
                         f"AI generated {new_alerts} appropriate alerts")
            return True
        else:
            self.log_test("Alert Generation Intelligence", False,
                         f"AI alert generation needs improvement: {new_alerts} alerts, "
                         f"{alerts_generated} expected")
            return False
    
    def run_ai_tests(self):
        """Run all AI system tests"""
        logger.info("🤖 Starting AI System Verification")
        logger.info("=" * 60)
        
        # Setup
        if not self.setup_test_tourist():
            logger.error("❌ Failed to setup test tourist")
            return False
        
        # Run tests
        tests = [
            ("Normal Behavior Detection", self.test_normal_behavior_detection),
            ("Speed Anomaly Detection", self.test_speed_anomaly_detection), 
            ("Geofence Intelligence", self.test_geofence_intelligence),
            ("Pattern Learning", self.test_pattern_learning),
            ("Alert Generation Intelligence", self.test_alert_generation_intelligence)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n🧪 Running: {test_name}")
            try:
                test_func()
                time.sleep(2)  # Pause between tests
            except Exception as e:
                self.log_test(test_name, False, f"Test execution failed: {e}")
        
        self.print_summary()
        return True
    
    def print_summary(self):
        """Print AI test summary"""
        logger.info("\n" + "=" * 60)
        logger.info("🤖 AI SYSTEM VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['success'])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"✅ Passed Tests: {passed}/{total}")
        logger.info(f"❌ Failed Tests: {total - passed}/{total}")
        logger.info(f"🧠 AI Intelligence Rate: {success_rate:.1f}%")
        
        # AI capabilities assessment
        ai_capabilities = {
            "Behavior Recognition": any("Behavior Detection" in r['test'] and r['success'] for r in self.test_results),
            "Anomaly Detection": any("Anomaly Detection" in r['test'] and r['success'] for r in self.test_results),
            "Spatial Intelligence": any("Geofence Intelligence" in r['test'] and r['success'] for r in self.test_results),
            "Pattern Learning": any("Pattern Learning" in r['test'] and r['success'] for r in self.test_results),
            "Smart Alerting": any("Alert Generation" in r['test'] and r['success'] for r in self.test_results)
        }
        
        logger.info(f"\n🧠 AI CAPABILITIES:")
        for capability, status in ai_capabilities.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"   {status_icon} {capability}")
        
        operational_rate = sum(1 for status in ai_capabilities.values() if status) / len(ai_capabilities) * 100
        
        if operational_rate >= 80:
            logger.info(f"\n🎉 AI SYSTEM IS HIGHLY INTELLIGENT! ({operational_rate:.0f}% operational)")
        elif operational_rate >= 60:
            logger.info(f"\n✅ AI SYSTEM IS FUNCTIONAL! ({operational_rate:.0f}% operational)")
        else:
            logger.warning(f"\n⚠️  AI SYSTEM NEEDS IMPROVEMENT! ({operational_rate:.0f}% operational)")

if __name__ == "__main__":
    tester = AISystemTester()
    tester.run_ai_tests()