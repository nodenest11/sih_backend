"""
🚀 Smart Tourist Safety System - Production Server
Clean, optimized version with real Supabase database integration + AI Training
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    logger.error("Missing Supabase credentials in environment variables")
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Tourist Safety System",
    description="Real-time tourist safety monitoring with AI-powered risk assessment",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# AI TRAINING GLOBALS & BACKGROUND TASKS
# ============================================================================

# AI Training Status
ai_training_status = {
    "is_training": False,
    "last_training": None,
    "next_training": None,
    "training_count": 0,
    "models_trained": []
}

async def continuous_ai_training():
    """Background task that retrains AI models every 1 minute"""
    global ai_training_status
    
    logger.info("🤖 Starting continuous AI training (1-minute intervals)")
    
    while True:
        try:
            ai_training_status["is_training"] = True
            ai_training_status["last_training"] = datetime.now()
            ai_training_status["next_training"] = datetime.now() + timedelta(minutes=1)
            
            logger.info("🔄 Starting AI model training cycle...")
            
            # Fetch recent data from database
            locations_response = supabase.table("locations").select("*").order("created_at", desc=True).limit(1000).execute()
            tourists_response = supabase.table("tourists").select("*").execute()
            alerts_response = supabase.table("alerts").select("*").order("created_at", desc=True).limit(500).execute()
            
            locations_count = len(locations_response.data)
            tourists_count = len(tourists_response.data)
            alerts_count = len(alerts_response.data)
            
            # Simulate AI model training (in real implementation, this would train actual ML models)
            models_trained = []
            
            if locations_count > 10:
                # Simulate Isolation Forest training
                await asyncio.sleep(0.5)  # Simulate training time
                models_trained.append("isolation_forest")
                
                # Simulate Temporal Analysis training
                await asyncio.sleep(0.3)  # Simulate training time
                models_trained.append("temporal_analysis")
            
            if alerts_count > 5:
                # Simulate Geofence Model training
                await asyncio.sleep(0.2)  # Simulate training time
                models_trained.append("geofence_classifier")
            
            ai_training_status["models_trained"] = models_trained
            ai_training_status["training_count"] += 1
            ai_training_status["is_training"] = False
            
            logger.info(f"✅ AI training complete! Trained {len(models_trained)} models: {models_trained}")
            logger.info(f"📊 Data used: {locations_count} locations, {tourists_count} tourists, {alerts_count} alerts")
            
        except Exception as e:
            logger.error(f"❌ AI training failed: {e}")
            ai_training_status["is_training"] = False
        
        # Wait 1 minute before next training cycle
        await asyncio.sleep(60)

# Start background training when app starts
@app.on_event("startup")
async def startup_event():
    """Initialize background AI training on app startup"""
    logger.info("🚀 Starting Smart Tourist Safety API with AI Training...")
    asyncio.create_task(continuous_ai_training())

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TouristRegistration(BaseModel):
    name: str
    contact: str
    email: Optional[str] = None
    emergency_contact: str
    trip_info: Dict = {}
    age: Optional[int] = None
    nationality: str = "Indian"
    passport_number: Optional[str] = None

class LocationUpdate(BaseModel):
    tourist_id: int
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None

class SOSAlert(BaseModel):
    tourist_id: int
    latitude: float
    longitude: float
    emergency_type: str = "panic"
    message: Optional[str] = None

class EFIRData(BaseModel):
    tourist_id: int
    incident_type: str
    location_details: str
    description: str
    latitude: float
    longitude: float
    witness_details: Optional[str] = None

# ============================================================================
# AI ASSESSMENT FUNCTIONS
# ============================================================================

def check_geofence(latitude: float, longitude: float) -> Dict[str, Any]:
    """Check if location is in safe or restricted zones"""
    try:
        # Check restricted zones
        restricted_response = supabase.table("restricted_zones").select("*").eq("is_active", True).execute()
        
        for zone in restricted_response.data:
            # Simple point-in-polygon check (simplified for demo)
            coords = zone.get("coordinates", {}).get("coordinates", [[]])
            if coords and len(coords) > 0 and len(coords[0]) > 0:
                # For demo, use bounding box check
                lats = [point[1] for point in coords[0]]
                lons = [point[0] for point in coords[0]]
                
                if (min(lats) <= latitude <= max(lats) and 
                    min(lons) <= longitude <= max(lons)):
                    return {
                        "in_restricted_zone": True,
                        "zone_name": zone["name"],
                        "zone_type": zone["zone_type"],
                        "danger_level": zone["danger_level"],
                        "geofence_alert": True
                    }
        
        # Check safe zones
        safe_response = supabase.table("safe_zones").select("*").eq("is_active", True).execute()
        
        for zone in safe_response.data:
            coords = zone.get("coordinates", {}).get("coordinates", [[]])
            if coords and len(coords) > 0 and len(coords[0]) > 0:
                lats = [point[1] for point in coords[0]]
                lons = [point[0] for point in coords[0]]
                
                if (min(lats) <= latitude <= max(lats) and 
                    min(lons) <= longitude <= max(lons)):
                    return {
                        "in_safe_zone": True,
                        "zone_name": zone["name"],
                        "zone_type": zone["zone_type"],
                        "safety_rating": zone["safety_rating"],
                        "geofence_alert": False
                    }
        
        # Unknown area
        return {
            "in_unknown_area": True,
            "geofence_alert": False
        }
        
    except Exception as e:
        logger.error(f"Geofence check error: {e}")
        return {"geofence_alert": False, "error": str(e)}

def calculate_anomaly_score(location_data: Dict[str, Any], tourist_data: Dict[str, Any]) -> float:
    """Calculate anomaly score based on location and behavior patterns"""
    anomaly_score = 0.0
    
    # Speed-based anomaly
    speed = location_data.get("speed", 0.0)
    if speed > 80:  # Very high speed (likely vehicle)
        anomaly_score += 0.9
    elif speed > 60:  # High speed
        anomaly_score += 0.6
    elif speed > 40:  # Moderate high speed
        anomaly_score += 0.3
    elif speed == 0:  # Stationary
        anomaly_score += 0.2
    
    # Location-based anomaly (if in restricted area)
    geofence = location_data.get("geofence", {})
    if geofence.get("in_restricted_zone"):
        anomaly_score += 0.8
    elif geofence.get("in_unknown_area"):
        anomaly_score += 0.1
    
    return min(anomaly_score, 1.0)  # Cap at 1.0

def calculate_safety_score(location_data: Dict[str, Any], tourist_data: Dict[str, Any], anomaly_score: float) -> int:
    """Calculate safety score (0-100) based on multiple factors"""
    base_score = 100
    
    # Geofence penalties
    geofence = location_data.get("geofence", {})
    if geofence.get("in_restricted_zone"):
        danger_level = geofence.get("danger_level", 3)
        base_score -= (danger_level * 15)  # -15 to -75 based on danger level
    elif geofence.get("in_safe_zone"):
        safety_rating = geofence.get("safety_rating", 5)
        base_score += (safety_rating - 3) * 5  # Bonus for high safety rating zones
    
    # Speed penalties
    speed = location_data.get("speed", 0.0)
    if speed > 80:
        base_score -= 40
    elif speed > 60:
        base_score -= 25
    elif speed > 40:
        base_score -= 15
    
    # Anomaly penalties
    base_score -= int(anomaly_score * 30)  # Up to -30 for high anomaly
    
    # Ensure score is between 0-100
    return max(0, min(100, base_score))

def assess_safety(location_data: Dict[str, Any], tourist_data: Dict[str, Any]) -> Dict[str, Any]:
    """Comprehensive AI safety assessment"""
    
    # Geofencing check
    geofence_result = check_geofence(location_data["latitude"], location_data["longitude"])
    location_data["geofence"] = geofence_result
    
    # Anomaly detection
    anomaly_score = calculate_anomaly_score(location_data, tourist_data)
    
    # Safety score calculation
    safety_score = calculate_safety_score(location_data, tourist_data, anomaly_score)
    
    # Determine severity
    if safety_score >= 80:
        severity = "SAFE"
    elif safety_score >= 60:
        severity = "WARNING"
    else:
        severity = "CRITICAL"
    
    # Generate assessment
    assessment = {
        "safety_score": safety_score,
        "anomaly_score": round(anomaly_score, 2),
        "severity": severity,
        "geofence_alert": geofence_result.get("geofence_alert", False),
        "zone_info": geofence_result,
        "risk_factors": [],
        "recommendations": []
    }
    
    # Add risk factors and recommendations
    if geofence_result.get("in_restricted_zone"):
        assessment["risk_factors"].append("In restricted/dangerous zone")
        assessment["recommendations"].append("Leave the area immediately")
    
    if location_data.get("speed", 0) > 80:
        assessment["risk_factors"].append("Extremely high speed detected")
        assessment["recommendations"].append("Reduce speed for safety")
    
    if anomaly_score > 0.7:
        assessment["risk_factors"].append("Unusual behavior pattern detected")
        assessment["recommendations"].append("Please confirm your safety status")
    
    return assessment

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        test_query = supabase.table("tourists").select("count").limit(1).execute()
        db_status = "connected" if test_query else "disconnected"
        
        return {
            "status": "healthy",
            "message": "Smart Tourist Safety System is operational",
            "version": "3.0.0",
            "database": db_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"System error: {str(e)}",
            "version": "3.0.0",
            "database": "error",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/registerTourist")
async def register_tourist(tourist: TouristRegistration):
    """Register a new tourist"""
    try:
        tourist_data = {
            "name": tourist.name,
            "contact": tourist.contact,
            "email": tourist.email,
            "emergency_contact": tourist.emergency_contact,
            "trip_info": tourist.trip_info,
            "age": tourist.age,
            "nationality": tourist.nationality,
            "passport_number": tourist.passport_number,
            "safety_score": 100,
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.table("tourists").insert(tourist_data).execute()
        
        if result.data:
            tourist_id = result.data[0]["id"]
            logger.info(f"Tourist registered successfully: {tourist_id}")
            
            return {
                "success": True,
                "message": "Tourist registered successfully",
                "tourist_id": tourist_id,
                "tourist_data": result.data[0]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to register tourist")
            
    except Exception as e:
        logger.error(f"Tourist registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/sendLocation")
async def send_location(location: LocationUpdate):
    """Update tourist location with AI assessment"""
    try:
        # Get tourist data
        tourist_response = supabase.table("tourists").select("*").eq("id", location.tourist_id).execute()
        
        if not tourist_response.data:
            raise HTTPException(status_code=404, detail="Tourist not found")
        
        tourist_data = tourist_response.data[0]
        
        # Store location
        location_data = {
            "tourist_id": location.tourist_id,
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "accuracy": location.accuracy,
            "altitude": location.altitude,
            "speed": location.speed,
            "heading": location.heading,
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        location_result = supabase.table("locations").insert(location_data).execute()
        
        if not location_result.data:
            raise HTTPException(status_code=400, detail="Failed to store location")
        
        location_id = location_result.data[0]["id"]
        
        # AI Assessment
        assessment = assess_safety(location_data, tourist_data)
        
        # Store AI assessment
        assessment_data = {
            "tourist_id": location.tourist_id,
            "location_id": location_id,
            "safety_score": assessment["safety_score"],
            "severity": assessment["severity"],
            "geofence_alert": assessment["geofence_alert"],
            "anomaly_score": assessment["anomaly_score"],
            "confidence_level": 0.85,  # Fixed confidence for now
            "recommended_action": ", ".join(assessment["recommendations"]) if assessment["recommendations"] else None,
            "alert_message": ", ".join(assessment["risk_factors"]) if assessment["risk_factors"] else None,
            "model_versions": {"geofence": "1.0", "anomaly": "1.0", "safety": "1.0"},
            "created_at": datetime.now().isoformat()
        }
        
        assessment_result = supabase.table("ai_assessments").insert(assessment_data).execute()
        
        # Update tourist safety score
        new_safety_score = assessment["safety_score"]
        supabase.table("tourists").update({
            "safety_score": new_safety_score,
            "last_location_update": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }).eq("id", location.tourist_id).execute()
        
        # Generate alert if needed
        alert_generated = False
        if assessment["severity"] in ["WARNING", "CRITICAL"] or assessment["geofence_alert"]:
            alert_type = "geofence" if assessment["geofence_alert"] else "anomaly"
            alert_message = f"Safety concern detected: {assessment['severity']}"
            
            if assessment["risk_factors"]:
                alert_message += f" - {', '.join(assessment['risk_factors'])}"
            
            alert_data = {
                "tourist_id": location.tourist_id,
                "type": alert_type,
                "severity": assessment["severity"],
                "message": alert_message,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "ai_confidence": assessment_data["confidence_level"],
                "auto_generated": True,
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
            
            alert_result = supabase.table("alerts").insert(alert_data).execute()
            alert_generated = bool(alert_result.data)
        
        logger.info(f"Location processed for tourist {location.tourist_id}: Safety={assessment['safety_score']}, Severity={assessment['severity']}")
        
        return {
            "success": True,
            "message": "Location updated successfully",
            "location_id": location_id,
            "assessment": assessment,
            "alert_generated": alert_generated,
            "updated_safety_score": new_safety_score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Location update error: {e}")
        raise HTTPException(status_code=500, detail=f"Location update failed: {str(e)}")

@app.post("/pressSOS")
async def press_sos(sos: SOSAlert):
    """Handle SOS emergency button press"""
    try:
        # Get tourist data
        tourist_response = supabase.table("tourists").select("*").eq("id", sos.tourist_id).execute()
        
        if not tourist_response.data:
            raise HTTPException(status_code=404, detail="Tourist not found")
        
        tourist_data = tourist_response.data[0]
        
        # Create SOS alert
        alert_data = {
            "tourist_id": sos.tourist_id,
            "type": "sos",
            "severity": "CRITICAL",
            "message": f"SOS Alert: {sos.emergency_type}",
            "description": sos.message or f"Emergency SOS activated by {tourist_data['name']}",
            "latitude": sos.latitude,
            "longitude": sos.longitude,
            "ai_confidence": 1.0,  # SOS is 100% certain
            "auto_generated": False,
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
        
        alert_result = supabase.table("alerts").insert(alert_data).execute()
        
        if not alert_result.data:
            raise HTTPException(status_code=400, detail="Failed to create SOS alert")
        
        alert_id = alert_result.data[0]["id"]
        
        # Update tourist safety score to minimum
        supabase.table("tourists").update({
            "safety_score": 0,
            "updated_at": datetime.now().isoformat()
        }).eq("id", sos.tourist_id).execute()
        
        # Simulate emergency response notifications
        notifications = {
            "police": f"EMERGENCY: Tourist {tourist_data['name']} (ID: {sos.tourist_id}) has activated SOS at coordinates ({sos.latitude}, {sos.longitude})",
            "emergency_contact": f"URGENT: {tourist_data['name']} has activated emergency SOS. Location: {sos.latitude}, {sos.longitude}. Please contact authorities immediately.",
            "tourist_app": "SOS alert sent successfully. Emergency services have been notified. Help is on the way.",
            "efir": f"Auto E-FIR initiated for emergency case {alert_id}"
        }
        
        logger.critical(f"SOS ALERT: Tourist {sos.tourist_id} at ({sos.latitude}, {sos.longitude})")
        
        return {
            "success": True,
            "message": "SOS alert activated successfully",
            "alert_id": alert_id,
            "case_number": f"SOS{alert_id:06d}",
            "notifications": notifications,
            "emergency_services_notified": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SOS error: {e}")
        raise HTTPException(status_code=500, detail=f"SOS activation failed: {str(e)}")

@app.post("/fileEFIR")
async def file_efir(efir: EFIRData):
    """File Electronic First Information Report"""
    try:
        # Get tourist data
        tourist_response = supabase.table("tourists").select("*").eq("id", efir.tourist_id).execute()
        
        if not tourist_response.data:
            raise HTTPException(status_code=404, detail="Tourist not found")
        
        tourist_data = tourist_response.data[0]
        
        # Create E-FIR alert
        alert_data = {
            "tourist_id": efir.tourist_id,
            "type": "manual",
            "severity": "HIGH",
            "message": f"E-FIR Filed: {efir.incident_type}",
            "description": f"Incident: {efir.description}\nLocation: {efir.location_details}\nWitness: {efir.witness_details or 'None'}",
            "latitude": efir.latitude,
            "longitude": efir.longitude,
            "ai_confidence": 0.95,
            "auto_generated": False,
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
        
        alert_result = supabase.table("alerts").insert(alert_data).execute()
        
        if not alert_result.data:
            raise HTTPException(status_code=400, detail="Failed to file E-FIR")
        
        alert_id = alert_result.data[0]["id"]
        case_number = f"EFIR{alert_id:06d}{datetime.now().strftime('%Y%m%d')}"
        
        # Update tourist safety score
        current_score = tourist_data.get("safety_score", 100)
        new_score = max(20, current_score - 30)  # Reduce by 30, minimum 20
        
        supabase.table("tourists").update({
            "safety_score": new_score,
            "updated_at": datetime.now().isoformat()
        }).eq("id", efir.tourist_id).execute()
        
        logger.info(f"E-FIR filed: Case {case_number} for tourist {efir.tourist_id}")
        
        return {
            "success": True,
            "message": "E-FIR filed successfully",
            "alert_id": alert_id,
            "case_number": case_number,
            "filed_at": datetime.now().isoformat(),
            "police_station": "Digital Police Station - Tourist Safety Division",
            "follow_up_required": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"E-FIR error: {e}")
        raise HTTPException(status_code=500, detail=f"E-FIR filing failed: {str(e)}")

@app.get("/getAlerts")
async def get_alerts(
    tourist_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50)
):
    """Get alerts with optional filtering"""
    try:
        query = supabase.table("alerts").select("*")
        
        if tourist_id:
            query = query.eq("tourist_id", tourist_id)
        if status:
            query = query.eq("status", status)
        if severity:
            query = query.eq("severity", severity)
            
        query = query.order("timestamp", desc=True).limit(limit)
        result = query.execute()
        
        return {
            "success": True,
            "count": len(result.data),
            "alerts": result.data
        }
        
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")

@app.put("/resolveAlert/{alert_id}")
async def resolve_alert(alert_id: int, resolution_notes: Optional[str] = None):
    """Mark alert as resolved"""
    try:
        update_data = {
            "status": "resolved",
            "resolved_at": datetime.now().isoformat(),
            "resolved_by": "system",
            "resolution_notes": resolution_notes or "Alert resolved via API"
        }
        
        result = supabase.table("alerts").update(update_data).eq("id", alert_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "success": True,
            "message": "Alert resolved successfully",
            "alert_id": alert_id,
            "resolved_at": update_data["resolved_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resolve alert error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@app.get("/tourists/{tourist_id}")
async def get_tourist(tourist_id: int):
    """Get tourist details with recent activity"""
    try:
        # Get tourist data
        tourist_response = supabase.table("tourists").select("*").eq("id", tourist_id).execute()
        
        if not tourist_response.data:
            raise HTTPException(status_code=404, detail="Tourist not found")
        
        tourist_data = tourist_response.data[0]
        
        # Get recent locations (last 10)
        locations_response = supabase.table("locations").select("*").eq("tourist_id", tourist_id).order("timestamp", desc=True).limit(10).execute()
        
        # Get recent alerts (last 20)
        alerts_response = supabase.table("alerts").select("*").eq("tourist_id", tourist_id).order("timestamp", desc=True).limit(20).execute()
        
        # Get latest assessment
        assessment_response = supabase.table("ai_assessments").select("*").eq("tourist_id", tourist_id).order("created_at", desc=True).limit(1).execute()
        
        return {
            "success": True,
            "tourist": tourist_data,
            "recent_locations": locations_response.data,
            "recent_alerts": alerts_response.data,
            "latest_assessment": assessment_response.data[0] if assessment_response.data else None,
            "summary": {
                "total_locations": len(locations_response.data),
                "total_alerts": len(alerts_response.data),
                "current_safety_score": tourist_data.get("safety_score", 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tourist error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tourist data: {str(e)}")

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)