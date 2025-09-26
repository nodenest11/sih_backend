"""
FastAPI router for AI/ML safety assessment endpoints
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from ai_ml.pipeline import TouristSafetyPipeline
from ai_ml.schemas.ai_schemas import TouristMovementData, SafetyAssessment
from schemas import LocationUpdate

# Initialize the AI/ML pipeline
ai_pipeline = TouristSafetyPipeline()

router = APIRouter()

class SafetyAssessmentRequest(BaseModel):
    """Request model for safety assessment"""
    tourist_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    speed: Optional[float] = None
    planned_route: Optional[List[Dict[str, Any]]] = None
    zone_type: Optional[str] = None

class SOSRequest(BaseModel):
    """Request model for SOS signal"""
    tourist_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    emergency_details: Optional[str] = None

class BatchAssessmentRequest(BaseModel):
    """Request model for batch safety assessment"""
    tourist_data: List[SafetyAssessmentRequest]

class ModelTrainingRequest(BaseModel):
    """Request model for model training"""
    training_data_source: str = "database"  # "database" or "file"
    include_historical_days: int = Field(default=30, ge=1, le=365)

@router.post("/assess-safety", response_model=Dict[str, Any])
async def assess_tourist_safety(request: SafetyAssessmentRequest):
    """
    Perform comprehensive AI/ML safety assessment for a tourist
    """
    try:
        # Convert request to TouristMovementData
        movement_data = TouristMovementData(
            tourist_id=request.tourist_id,
            latitude=request.latitude,
            longitude=request.longitude,
            altitude=request.altitude,
            timestamp=datetime.now(),
            speed=request.speed,
            planned_route=request.planned_route,
            zone_type=request.zone_type
        )
        
        # Perform safety assessment
        assessment = ai_pipeline.assess_tourist_safety(movement_data)
        
        # Convert to response format
        response = {
            "tourist_id": assessment.tourist_id,
            "timestamp": assessment.timestamp.isoformat(),
            "safety_score": assessment.safety_score,
            "risk_level": assessment.risk_level,
            "should_alert_tourist": assessment.should_alert_tourist,
            "should_alert_authorities": assessment.should_alert_authorities,
            "alert_message": assessment.alert_message,
            "location": assessment.location,
            "zone_info": assessment.zone_info,
            "model_results": {
                "geofencing": assessment.geofence_result,
                "anomaly_detection": assessment.anomaly_result,
                "temporal_analysis": assessment.temporal_result
            }
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing safety assessment: {str(e)}"
        )

@router.post("/sos-alert", response_model=Dict[str, Any])
async def handle_sos_alert(request: SOSRequest):
    """
    Handle emergency SOS signal from tourist
    """
    try:
        # Create additional context for SOS
        additional_info = {
            "emergency_details": request.emergency_details,
            "sos_timestamp": datetime.now()
        }
        
        # Process SOS signal
        assessment = ai_pipeline.handle_sos_signal(
            tourist_id=request.tourist_id,
            latitude=request.latitude,
            longitude=request.longitude,
            additional_info=additional_info
        )
        
        # Convert to response format
        response = {
            "emergency_id": f"SOS_{request.tourist_id}_{int(datetime.now().timestamp())}",
            "tourist_id": assessment.tourist_id,
            "timestamp": assessment.timestamp.isoformat(),
            "safety_score": assessment.safety_score,
            "risk_level": assessment.risk_level,
            "location": assessment.location,
            "alert_message": assessment.alert_message,
            "emergency_response_required": True,
            "authorities_notified": assessment.should_alert_authorities
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing SOS alert: {str(e)}"
        )

@router.post("/batch-assess", response_model=List[Dict[str, Any]])
async def batch_assess_safety(request: BatchAssessmentRequest):
    """
    Perform safety assessment for multiple tourists
    """
    try:
        # Convert requests to TouristMovementData
        movement_data_list = []
        for req in request.tourist_data:
            movement_data = TouristMovementData(
                tourist_id=req.tourist_id,
                latitude=req.latitude,
                longitude=req.longitude,
                altitude=req.altitude,
                timestamp=datetime.now(),
                speed=req.speed,
                planned_route=req.planned_route,
                zone_type=req.zone_type
            )
            movement_data_list.append(movement_data)
        
        # Perform batch assessment
        assessments = ai_pipeline.batch_assess_safety(movement_data_list)
        
        # Convert to response format
        responses = []
        for assessment in assessments:
            response = {
                "tourist_id": assessment.tourist_id,
                "safety_score": assessment.safety_score,
                "risk_level": assessment.risk_level,
                "should_alert_tourist": assessment.should_alert_tourist,
                "should_alert_authorities": assessment.should_alert_authorities,
                "alert_message": assessment.alert_message,
                "location": assessment.location
            }
            responses.append(response)
            
        return responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing batch assessment: {str(e)}"
        )

@router.get("/pipeline-status", response_model=Dict[str, Any])
async def get_pipeline_status():
    """
    Get status of the AI/ML pipeline and all models
    """
    try:
        status_info = ai_pipeline.get_pipeline_status()
        return status_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving pipeline status: {str(e)}"
        )

@router.post("/train-models")
async def train_models(request: ModelTrainingRequest, background_tasks: BackgroundTasks):
    """
    Train AI/ML models with available data (runs in background)
    """
    try:
        # Add training task to background tasks
        background_tasks.add_task(
            _train_models_background,
            request.training_data_source,
            request.include_historical_days
        )
        
        return {
            "message": "Model training started in background",
            "training_data_source": request.training_data_source,
            "include_historical_days": request.include_historical_days,
            "started_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting model training: {str(e)}"
        )

@router.get("/zone-info/{latitude}/{longitude}")
async def get_zone_info(latitude: float, longitude: float):
    """
    Get zone information for a specific location
    """
    try:
        zone_info = ai_pipeline.geofence_model.get_zone_info(latitude, longitude)
        return zone_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving zone information: {str(e)}"
        )

@router.get("/tourist-history/{tourist_id}")
async def get_tourist_history(tourist_id: int):
    """
    Get cached feature history for a tourist
    """
    try:
        history = ai_pipeline.get_tourist_history(tourist_id)
        
        # Convert to serializable format
        history_data = []
        for features in history:
            feature_dict = {
                "timestamp": features.timestamp.isoformat(),
                "location": {
                    "latitude": features.latitude,
                    "longitude": features.longitude
                },
                "features": {
                    "distance_per_min": features.distance_per_min,
                    "inactivity_duration": features.inactivity_duration,
                    "deviation_from_route": features.deviation_from_route,
                    "speed": features.speed
                },
                "zone_type": features.zone_type
            }
            history_data.append(feature_dict)
            
        return {
            "tourist_id": tourist_id,
            "feature_count": len(history_data),
            "history": history_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tourist history: {str(e)}"
        )

@router.post("/clear-cache")
async def clear_cache(tourist_id: Optional[int] = None):
    """
    Clear feature cache for a specific tourist or all tourists
    """
    try:
        ai_pipeline.clear_cache(tourist_id)
        
        message = f"Cache cleared for tourist {tourist_id}" if tourist_id else "All caches cleared"
        
        return {
            "message": message,
            "cleared_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )

@router.get("/model-metrics")
async def get_model_metrics():
    """
    Get performance metrics for all AI/ML models
    """
    try:
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "models": {
                "geofencing": {
                    "type": "rule_based",
                    "status": "active",
                    "zones": {
                        "restricted": len(ai_pipeline.geofence_model.restricted_zones),
                        "risky": len(ai_pipeline.geofence_model.risky_zones),
                        "safe": len(ai_pipeline.geofence_model.safe_zones)
                    }
                },
                "anomaly_detector": ai_pipeline.anomaly_detector.get_model_info(),
                "temporal_detector": ai_pipeline.temporal_detector.get_model_info()
            }
        }
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving model metrics: {str(e)}"
        )

async def _train_models_background(training_data_source: str, include_historical_days: int):
    """
    Background task for model training
    """
    try:
        print(f"Starting model training from {training_data_source}")
        
        # In a real implementation, this would:
        # 1. Fetch training data from database or file
        # 2. Prepare features using FeatureExtractor
        # 3. Train models using the pipeline
        # 4. Save trained models
        # 5. Update model status
        
        # For now, we'll create a placeholder
        training_features = []  # This would be populated from database
        
        if training_features:
            results = ai_pipeline.train_models(training_features)
            saved_paths = ai_pipeline.save_models()
            
            print(f"Model training completed. Results: {results}")
            print(f"Models saved to: {saved_paths}")
        else:
            print("No training data available")
            
    except Exception as e:
        print(f"Error in background model training: {e}")