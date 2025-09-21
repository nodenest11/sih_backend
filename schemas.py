from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import AlertType, AlertStatus

# Tourist Schemas
class TouristCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    contact: str = Field(..., min_length=10, max_length=20)
    trip_info: Optional[str] = None
    emergency_contact: str = Field(..., min_length=10, max_length=20)

class TouristResponse(BaseModel):
    id: int
    name: str
    contact: str
    trip_info: Optional[str]
    emergency_contact: str
    safety_score: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Location Schemas
class LocationUpdate(BaseModel):
    tourist_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class LocationResponse(BaseModel):
    id: int
    tourist_id: int
    latitude: float
    longitude: float
    timestamp: datetime
    tourist_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Alert Schemas
class PanicAlertCreate(BaseModel):
    tourist_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class GeofenceAlertCreate(BaseModel):
    tourist_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    zone_name: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    tourist_id: int
    type: AlertType
    message: str
    latitude: Optional[float]
    longitude: Optional[float]
    timestamp: datetime
    status: AlertStatus
    resolved_at: Optional[datetime]
    tourist_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Safety Score Update Schema
class SafetyScoreUpdate(BaseModel):
    tourist_id: int
    score_change: int
    reason: str

# Heatmap Schemas
class HeatmapPoint(BaseModel):
    latitude: float
    longitude: float
    intensity: int = 1
    tourist_count: Optional[int] = None
    alert_count: Optional[int] = None
    risk_level: Optional[str] = None

class HeatmapResponse(BaseModel):
    points: List[HeatmapPoint]
    total_points: int
    bounds: dict  # {"north": lat, "south": lat, "east": lng, "west": lng}
    generated_at: datetime