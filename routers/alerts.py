from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Alert, Tourist, AlertType, AlertStatus, RestrictedZone
from schemas import PanicAlertCreate, GeofenceAlertCreate, AlertResponse
from typing import List
from datetime import datetime
import json

router = APIRouter()

def check_geofence_violation(latitude: float, longitude: float, db: Session) -> tuple:
    """Check if coordinates are within any restricted zone"""
    zones = db.query(RestrictedZone).all()
    
    for zone in zones:
        try:
            # Parse polygon coordinates from JSON string
            polygon_coords = json.loads(zone.polygon_coordinates)
            
            # Simple point-in-polygon check (ray casting algorithm)
            if point_in_polygon(latitude, longitude, polygon_coords):
                return True, zone.name, zone.risk_level
        except (json.JSONDecodeError, Exception):
            continue
    
    return False, None, 0

def point_in_polygon(lat: float, lon: float, polygon: List[List[float]]) -> bool:
    """Check if point is inside polygon using ray casting algorithm"""
    x, y = lat, lon
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

@router.post("/panic", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_panic_alert(alert_data: PanicAlertCreate, db: Session = Depends(get_db)):
    """Create a panic alert"""
    # Check if tourist exists
    tourist = db.query(Tourist).filter(Tourist.id == alert_data.tourist_id).first()
    if not tourist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    
    # Create panic alert
    db_alert = Alert(
        tourist_id=alert_data.tourist_id,
        type=AlertType.panic,
        message=f"PANIC ALERT: {tourist.name} has triggered a panic alert at coordinates ({alert_data.latitude}, {alert_data.longitude})",
        latitude=alert_data.latitude,
        longitude=alert_data.longitude,
        status=AlertStatus.active
    )
    
    db.add(db_alert)
    
    # Update safety score (panic = -40 points)
    tourist.safety_score = max(0, tourist.safety_score - 40)
    
    db.commit()
    db.refresh(db_alert)
    
    # Add tourist name to response
    response = AlertResponse.from_orm(db_alert)
    response.tourist_name = tourist.name
    
    return response

@router.post("/geofence", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_geofence_alert(alert_data: GeofenceAlertCreate, db: Session = Depends(get_db)):
    """Create a geofence violation alert"""
    # Check if tourist exists
    tourist = db.query(Tourist).filter(Tourist.id == alert_data.tourist_id).first()
    if not tourist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    
    # Check if location is in restricted zone
    is_in_zone, zone_name, risk_level = check_geofence_violation(
        alert_data.latitude, alert_data.longitude, db
    )
    
    if not is_in_zone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is not in a restricted zone"
        )
    
    # Create geofence alert
    zone_display_name = alert_data.zone_name or zone_name
    db_alert = Alert(
        tourist_id=alert_data.tourist_id,
        type=AlertType.geofence,
        message=f"GEOFENCE VIOLATION: {tourist.name} has entered restricted zone '{zone_display_name}' at coordinates ({alert_data.latitude}, {alert_data.longitude})",
        latitude=alert_data.latitude,
        longitude=alert_data.longitude,
        status=AlertStatus.active
    )
    
    db.add(db_alert)
    
    # Update safety score (geofence violation = -20 points)
    tourist.safety_score = max(0, tourist.safety_score - 20)
    
    db.commit()
    db.refresh(db_alert)
    
    # Add tourist name to response
    response = AlertResponse.from_orm(db_alert)
    response.tourist_name = tourist.name
    
    return response

@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    status_filter: str = "active", 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get alerts with optional status filter"""
    query = db.query(Alert, Tourist.name).join(Tourist, Alert.tourist_id == Tourist.id)
    
    if status_filter == "active":
        query = query.filter(Alert.status == AlertStatus.active)
    elif status_filter == "resolved":
        query = query.filter(Alert.status == AlertStatus.resolved)
    # If status_filter is "all" or any other value, don't filter by status
    
    alerts_with_names = query.order_by(desc(Alert.timestamp)).limit(limit).all()
    
    # Format response
    result = []
    for alert, tourist_name in alerts_with_names:
        alert_response = AlertResponse.from_orm(alert)
        alert_response.tourist_name = tourist_name
        result.append(alert_response)
    
    return result

@router.put("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert.status == AlertStatus.resolved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert is already resolved"
        )
    
    # Update alert status
    alert.status = AlertStatus.resolved
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    # Get tourist name for response
    tourist = db.query(Tourist).filter(Tourist.id == alert.tourist_id).first()
    response = AlertResponse.from_orm(alert)
    response.tourist_name = tourist.name if tourist else None
    
    return response

@router.get("/tourist/{tourist_id}", response_model=List[AlertResponse])
def get_tourist_alerts(
    tourist_id: int, 
    status_filter: str = "all", 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """Get alerts for a specific tourist"""
    # Check if tourist exists
    tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
    if not tourist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    
    query = db.query(Alert).filter(Alert.tourist_id == tourist_id)
    
    if status_filter == "active":
        query = query.filter(Alert.status == AlertStatus.active)
    elif status_filter == "resolved":
        query = query.filter(Alert.status == AlertStatus.resolved)
    
    alerts = query.order_by(desc(Alert.timestamp)).limit(limit).all()
    
    # Add tourist name to each response
    result = []
    for alert in alerts:
        alert_response = AlertResponse.from_orm(alert)
        alert_response.tourist_name = tourist.name
        result.append(alert_response)
    
    return result