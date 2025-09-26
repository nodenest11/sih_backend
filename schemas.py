from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

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
    
    class Config:
        from_attributes = True

class PanicAlertCreate(BaseModel):
    tourist_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class GeofenceAlertCreate(BaseModel):
    tourist_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    zone_name: str

class AlertResponse(BaseModel):
    id: int
    tourist_id: int
    type: str
    message: str
    timestamp: datetime
    status: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    class Config:
        from_attributes = True

class DatabaseInitResponse(BaseModel):
    message: str
    restricted_zones_created: int

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    supabase: str