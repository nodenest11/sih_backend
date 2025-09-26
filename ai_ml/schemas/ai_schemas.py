"""
Data schemas for AI/ML pipeline
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class TouristMovementData(BaseModel):
    """Raw tourist movement data from backend"""
    tourist_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    timestamp: datetime
    speed: Optional[float] = None  # m/s or km/h
    planned_route: Optional[List[Dict[str, Any]]] = None  # List of waypoints
    zone_type: Optional[str] = None  # safe, risky, restricted

class ProcessedFeatures(BaseModel):
    """Processed features for ML models"""
    tourist_id: int
    timestamp: datetime
    
    # Raw features
    latitude: float
    longitude: float
    speed: float
    zone_type: str
    
    # Derived features
    distance_per_min: float
    inactivity_duration: float  # minutes
    deviation_from_route: float  # meters
    
    # Historical context
    recent_locations: List[Dict[str, Any]]

class ModelPrediction(BaseModel):
    """Individual model prediction result"""
    model_name: str
    score: float  # 0-1 normalized score
    confidence: float  # 0-1 confidence level
    details: Dict[str, Any]
    timestamp: datetime

class SafetyAssessment(BaseModel):
    """Final safety assessment result"""
    tourist_id: int
    timestamp: datetime
    
    # Overall safety score (0-100)
    safety_score: float
    risk_level: str  # "safe", "warning", "critical"
    
    # Individual model results
    geofence_result: Dict[str, Any]
    anomaly_result: Dict[str, Any]
    temporal_result: Dict[str, Any]
    
    # Alert information
    should_alert_tourist: bool
    should_alert_authorities: bool
    alert_message: Optional[str] = None
    
    # Additional context
    location: Dict[str, float]  # lat, lon
    zone_info: Dict[str, Any]

class TrainingData(BaseModel):
    """Data format for model training"""
    features: List[ProcessedFeatures]
    labels: Optional[List[str]] = None  # For supervised learning (future)
    incident_reports: Optional[List[Dict[str, Any]]] = None

class ModelMetrics(BaseModel):
    """Model performance metrics"""
    model_name: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    auc_score: Optional[float] = None
    timestamp: datetime