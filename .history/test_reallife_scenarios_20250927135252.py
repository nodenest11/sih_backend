"""
🌍 Real-Life Tourist Scenario Test
Comprehensive realistic tourist journey simulation with multiple scenarios
"""

import requests
import json
import logging
from datetime import datetime, timedelta
import time
import random

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"
TIMEOUT = 15

class RealLifeScenarioTester:
    def __init__(self):
        self.session = requests.Session()
        self.scenarios_results = []
        
    def log_scenario(self, scenario_name: str, success: bool, details: str = "", data: dict = None):
        """Log scenario results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {scenario_name}")
        if details:
            logger.info(f"   📋 {details}")
        if data:
            logger.info(f"   📊 Final State: Safety={data.get('safety_score')}, "
                      f"Alerts={data.get('total_alerts')}")
        
        self.scenarios_results.append({
            "scenario": scenario_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def create_tourist(self, name: str, contact: str, trip_info: dict) -> int:
        """Create a tourist for scenario testing"""
        tourist_data = {
            "name": name,
            "contact": contact,
            "email": f"{name.lower().replace(' ', '')}@email.com",
            "emergency_contact": "+91-9876543210",
            "trip_info": trip_info,
            "age": random.randint(20, 65),
            "nationality": random.choice(["Indian", "American", "British", "German", "Japanese"])
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/registerTourist", 
                                       json=tourist_data, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                tourist_id = data.get('tourist_id')
                logger.info(f"✅ Created tourist: {name} (ID: {tourist_id})")
                return tourist_id
            else:
                logger.error(f"❌ Failed to create tourist: {name}")
                return None
        except Exception as e:
            logger.error(f"❌ Tourist creation error: {e}")
            return None
    
    def send_location(self, tourist_id: int, lat: float, lon: float, speed: float, desc: str = ""):
        """Send location update and return assessment"""
        location_data = {
            "tourist_id": tourist_id,
            "latitude": lat,
            "longitude": lon,
            "speed": speed,
            "accuracy": 5.0,
            "heading": random.randint(0, 360)
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/sendLocation", 
                                       json=location_data, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                assessment = data.get('assessment', {})
                
                if desc:
                    logger.info(f"   📍 {desc}: Safety={assessment.get('safety_score')}, "
                              f"Severity={assessment.get('severity')}, "
                              f"Alert={data.get('alert_generated', False)}")
                
                return assessment
            else:
                logger.error(f"   ❌ Failed to send location: {desc}")
                return None
        except Exception as e:
            logger.error(f"   ❌ Location error: {e}")
            return None
    
    def get_tourist_summary(self, tourist_id: int) -> dict:
        """Get tourist summary with stats"""
        try:
            response = self.session.get(f"{BASE_URL}/tourists/{tourist_id}", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                tourist = data.get('tourist', {})
                summary = data.get('summary', {})
                
                return {
                    "name": tourist.get('name'),
                    "safety_score": tourist.get('safety_score'),
                    "total_locations": summary.get('total_locations'),
                    "total_alerts": summary.get('total_alerts'),
                    "recent_alerts": data.get('recent_alerts', [])
                }
            else:
                logger.error(f"   ❌ Failed to get tourist summary")
                return {}
        except Exception as e:
            logger.error(f"   ❌ Summary error: {e}")
            return {}
    
    def scenario_normal_tourist_day(self):
        """Scenario 1: Normal tourist exploring Delhi"""
        logger.info("\n🗺️ SCENARIO 1: Normal Tourist Day in Delhi")
        logger.info("=" * 50)
        
        tourist_id = self.create_tourist(
            "Alice Johnson", 
            "+1-555-0123",
            {
                "destination": "Delhi",
                "duration": 3,
                "purpose": "Sightseeing",
                "planned_places": ["India Gate", "Red Fort", "Qutub Minar"]
            }
        )
        
        if not tourist_id:
            self.log_scenario("Normal Tourist Day", False, "Failed to create tourist")
            return
        
        # Normal tourist journey
        journey = [
            {"lat": 28.6129, "lon": 77.2295, "speed": 0.0, "desc": "Arrived at India Gate (stationary)"},
            {"lat": 28.6135, "lon": 77.2300, "speed": 2.5, "desc": "Walking around India Gate"},
            {"lat": 28.6140, "lon": 77.2305, "speed": 3.0, "desc": "Moving towards monuments"},
            {"lat": 28.6130, "lon": 77.2290, "speed": 2.0, "desc": "Taking photos"},
            {"lat": 28.6200, "lon": 77.2350, "speed": 15.0, "desc": "Taking auto-rickshaw"},
            {"lat": 28.6300, "lon": 77.2180, "speed": 20.0, "desc": "Moving to Connaught Place"},
            {"lat": 28.6304, "lon": 77.2177, "speed": 0.0, "desc": "Shopping at CP"},
            {"lat": 28.6310, "lon": 77.2185, "speed": 2.5, "desc": "Walking in CP market"},
        ]
        
        for step in journey:
            assessment = self.send_location(tourist_id, step["lat"], step["lon"], 
                                          step["speed"], step["desc"])
            if not assessment:
                self.log_scenario("Normal Tourist Day", False, "Location update failed")
                return
            time.sleep(0.5)
        
        # Get final summary
        summary = self.get_tourist_summary(tourist_id)
        
        # Evaluate scenario
        if (summary.get('safety_score', 0) >= 80 and 
            summary.get('total_alerts', 0) <= 2):  # Minimal alerts for normal behavior
            self.log_scenario("Normal Tourist Day", True, 
                           f"Tourist had safe day with minimal alerts", summary)
        else:
            self.log_scenario("Normal Tourist Day", False, 
                           f"Unexpected alerts for normal behavior", summary)
    
    def scenario_emergency_situation(self):
        """Scenario 2: Tourist in emergency situation"""
        logger.info("\n🚨 SCENARIO 2: Tourist Emergency Situation")
        logger.info("=" * 50)
        
        tourist_id = self.create_tourist(
            "Bob Martinez", 
            "+34-666-789012",
            {
                "destination": "Delhi", 
                "duration": 2,
                "purpose": "Business",
                "hotel": "Hotel near CP"
            }
        )
        
        if not tourist_id:
            self.log_scenario("Emergency Situation", False, "Failed to create tourist")
            return
        
        # Emergency scenario progression
        journey = [
            {"lat": 28.6304, "lon": 77.2177, "speed": 3.0, "desc": "Normal walking at CP"},
            {"lat": 28.6280, "lon": 77.2160, "speed": 1.0, "desc": "Walking slower (feeling unsafe)"},
            {"lat": 28.6260, "lon": 77.2180, "speed": 0.5, "desc": "Very slow movement (distressed)"},
            {"lat": 28.6250, "lon": 77.2170, "speed": 0.0, "desc": "Stopped (in trouble)"},
        ]
        
        for step in journey:
            assessment = self.send_location(tourist_id, step["lat"], step["lon"], 
                                          step["speed"], step["desc"])
            if not assessment:
                self.log_scenario("Emergency Situation", False, "Location update failed")
                return
            time.sleep(0.5)
        
        # Tourist presses SOS
        logger.info("   🆘 Tourist presses SOS button...")
        sos_data = {
            "tourist_id": tourist_id,
            "latitude": 28.6250,
            "longitude": 77.2170,
            "emergency_type": "help_needed",
            "message": "Being followed, need immediate help!"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/pressSOS", json=sos_data, timeout=TIMEOUT)
            if response.status_code == 200:
                sos_result = response.json()
                alert_id = sos_result.get('alert_id')
                logger.info(f"   ✅ SOS Alert created: {alert_id}")
                
                # File E-FIR
                logger.info("   📝 Filing E-FIR...")
                efir_data = {
                    "tourist_id": tourist_id,
                    "incident_type": "harassment", 
                    "location_details": "Near Connaught Place Metro Station",
                    "description": "Tourist was being followed and felt threatened",
                    "latitude": 28.6250,
                    "longitude": 77.2170,
                    "witness_details": "Local shopkeepers witnessed the incident"
                }
                
                efir_response = self.session.post(f"{BASE_URL}/fileEFIR", 
                                                json=efir_data, timeout=TIMEOUT)
                if efir_response.status_code == 200:
                    efir_result = efir_response.json()
                    case_number = efir_result.get('case_number')
                    logger.info(f"   ✅ E-FIR filed: {case_number}")
                else:
                    logger.error("   ❌ Failed to file E-FIR")
            else:
                logger.error("   ❌ SOS failed")
                self.log_scenario("Emergency Situation", False, "SOS activation failed")
                return
        except Exception as e:
            logger.error(f"   ❌ Emergency handling error: {e}")
            self.log_scenario("Emergency Situation", False, str(e))
            return
        
        # Get final summary
        summary = self.get_tourist_summary(tourist_id)
        
        # Evaluate emergency response
        if (summary.get('safety_score', 100) <= 20 and  # Should be very low after emergency
            summary.get('total_alerts', 0) >= 2):       # Should have multiple alerts
            self.log_scenario("Emergency Situation", True, 
                           "Emergency properly handled with alerts and E-FIR", summary)
        else:
            self.log_scenario("Emergency Situation", False, 
                           "Emergency response insufficient", summary)
    
    def scenario_risky_behavior_tourist(self):
        """Scenario 3: Tourist exhibiting risky behavior"""
        logger.info("\n⚠️ SCENARIO 3: Tourist with Risky Behavior")
        logger.info("=" * 50)
        
        tourist_id = self.create_tourist(
            "Charlie Wild",
            "+44-789-456123", 
            {
                "destination": "Delhi",
                "duration": 1,
                "purpose": "Adventure",
                "risk_profile": "High"
            }
        )
        
        if not tourist_id:
            self.log_scenario("Risky Behavior Tourist", False, "Failed to create tourist")
            return
        
        # Risky behavior journey
        risky_journey = [
            {"lat": 28.6129, "lon": 77.2295, "speed": 5.0, "desc": "Started at India Gate"},
            {"lat": 28.6200, "lon": 77.2350, "speed": 45.0, "desc": "High speed movement (motorcycle?)"},
            {"lat": 28.6400, "lon": 77.2380, "speed": 75.0, "desc": "Very high speed (dangerous driving)"},
            {"lat": 28.6500, "lon": 77.2400, "speed": 85.0, "desc": "Extreme speed (reckless behavior)"},
            {"lat": 28.654, "lon": 77.241, "speed": 15.0, "desc": "Slowing down near restricted area"},
            {"lat": 28.656, "lon": 77.242, "speed": 0.0, "desc": "Entered restricted military zone"},
            {"lat": 28.657, "lon": 77.242, "speed": 3.0, "desc": "Moving inside restricted zone"},
        ]
        
        for step in risky_journey:
            assessment = self.send_location(tourist_id, step["lat"], step["lon"], 
                                          step["speed"], step["desc"])
            if not assessment:
                self.log_scenario("Risky Behavior Tourist", False, "Location update failed")
                return
            time.sleep(0.5)
        
        # Get final summary
        summary = self.get_tourist_summary(tourist_id)
        
        # Evaluate AI response to risky behavior
        if (summary.get('safety_score', 100) <= 40 and   # Should be low due to risky behavior
            summary.get('total_alerts', 0) >= 3):        # Should generate multiple alerts
            self.log_scenario("Risky Behavior Tourist", True,
                           "AI correctly identified and alerted on risky behavior", summary)
        else:
            self.log_scenario("Risky Behavior Tourist", False,
                           "AI didn't properly detect risky behavior", summary)
    
    def scenario_group_tourists(self):
        """Scenario 4: Group of tourists with different behaviors"""
        logger.info("\n👥 SCENARIO 4: Group of Tourists")
        logger.info("=" * 50)
        
        # Create group of 3 tourists
        group = []
        tourist_names = ["David Leader", "Emma Follower", "Frank Explorer"]
        
        for name in tourist_names:
            tourist_id = self.create_tourist(
                name,
                f"+1-555-{random.randint(1000, 9999)}",
                {
                    "destination": "Delhi",
                    "duration": 2,
                    "purpose": "Group Tourism",
                    "group_size": 3
                }
            )
            if tourist_id:
                group.append({"name": name, "id": tourist_id})
        
        if len(group) != 3:
            self.log_scenario("Group Tourists", False, "Failed to create complete group")
            return
        
        # Simulate group movement with one member getting separated
        base_locations = [
            {"lat": 28.6129, "lon": 77.2295, "desc": "Group at India Gate"},
            {"lat": 28.6140, "lon": 77.2305, "desc": "Group walking together"},
            {"lat": 28.6150, "lon": 77.2315, "desc": "Group taking photos"},
        ]
        
        # Normal group movement
        for i, location in enumerate(base_locations):
            for member in group:
                # Add small variation for each member
                lat_offset = random.uniform(-0.0005, 0.0005)
                lon_offset = random.uniform(-0.0005, 0.0005)
                
                assessment = self.send_location(
                    member["id"],
                    location["lat"] + lat_offset,
                    location["lon"] + lon_offset,
                    2.5,  # Normal walking speed
                    f"{member['name']} - {location['desc']}"
                )
                time.sleep(0.2)
        
        # Frank gets separated and exhibits risky behavior
        logger.info("   ⚠️ Frank Explorer gets separated from group...")
        separated_journey = [
            {"lat": 28.6200, "lon": 77.2400, "speed": 8.0, "desc": "Frank walking fast (lost)"},
            {"lat": 28.6300, "lon": 77.2500, "speed": 25.0, "desc": "Frank taking taxi (panicked)"},
            {"lat": 28.6500, "lon": 77.2400, "speed": 60.0, "desc": "Frank in fast vehicle (trying to find group)"},
        ]
        
        frank_id = next(member["id"] for member in group if "Frank" in member["name"])
        for step in separated_journey:
            assessment = self.send_location(frank_id, step["lat"], step["lon"], 
                                          step["speed"], step["desc"])
            time.sleep(0.5)
        
        # Get summaries for all group members
        group_summaries = []
        for member in group:
            summary = self.get_tourist_summary(member["id"])
            summary["name"] = member["name"]
            group_summaries.append(summary)
            logger.info(f"   👤 {summary['name']}: Safety={summary.get('safety_score')}, "
                      f"Alerts={summary.get('total_alerts')}")
        
        # Evaluate group scenario
        frank_summary = next(s for s in group_summaries if "Frank" in s["name"])
        others_avg_safety = sum(s.get("safety_score", 0) for s in group_summaries 
                               if "Frank" not in s["name"]) / 2
        
        if (frank_summary.get("safety_score", 100) < others_avg_safety - 20 and
            frank_summary.get("total_alerts", 0) >= 1):
            self.log_scenario("Group Tourists", True,
                           "AI correctly identified separated member with different risk level")
        else:
            self.log_scenario("Group Tourists", False,
                           "AI didn't properly track group dynamics")
    
    def run_all_scenarios(self):
        """Run all real-life scenarios"""
        logger.info("🌍 Starting Real-Life Tourist Scenario Testing")
        logger.info("=" * 70)
        
        scenarios = [
            ("Normal Tourist Day", self.scenario_normal_tourist_day),
            ("Emergency Situation", self.scenario_emergency_situation),
            ("Risky Behavior Tourist", self.scenario_risky_behavior_tourist),
            ("Group Tourists", self.scenario_group_tourists),
        ]
        
        for scenario_name, scenario_func in scenarios:
            try:
                scenario_func()
                time.sleep(2)  # Pause between scenarios
            except Exception as e:
                self.log_scenario(scenario_name, False, f"Scenario execution failed: {e}")
        
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print comprehensive scenario testing summary"""
        logger.info("\n" + "=" * 70)
        logger.info("🌍 REAL-LIFE SCENARIOS COMPREHENSIVE SUMMARY")
        logger.info("=" * 70)
        
        passed = sum(1 for r in self.scenarios_results if r['success'])
        total = len(self.scenarios_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"✅ Passed Scenarios: {passed}/{total}")
        logger.info(f"❌ Failed Scenarios: {total - passed}/{total}")
        logger.info(f"🎯 Real-World Readiness: {success_rate:.1f}%")
        
        # Detailed results
        logger.info(f"\n📋 Scenario Results:")
        for result in self.scenarios_results:
            status_icon = "✅" if result['success'] else "❌"
            logger.info(f"   {status_icon} {result['scenario']}: {result['details']}")
        
        # System readiness assessment
        if success_rate >= 90:
            logger.info(f"\n🎉 SYSTEM IS PRODUCTION READY! Excellent real-world performance!")
        elif success_rate >= 75:
            logger.info(f"\n✅ SYSTEM IS READY FOR DEPLOYMENT! Good real-world handling!")
        elif success_rate >= 50:
            logger.info(f"\n⚠️  SYSTEM NEEDS MINOR IMPROVEMENTS before deployment!")
        else:
            logger.warning(f"\n❌ SYSTEM REQUIRES SIGNIFICANT IMPROVEMENTS!")

if __name__ == "__main__":
    tester = RealLifeScenarioTester()
    tester.run_all_scenarios()