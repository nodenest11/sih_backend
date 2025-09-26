from fastapi import APIRouter, HTTPException, status
from schemas import PanicAlertCreate, GeofenceAlertCreate, AlertResponse
from services import AlertService
from typing import List

router = APIRouter()

@router.post("/panic", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_panic_alert(alert: PanicAlertCreate):
    """Create a panic alert"""
    try:
        result = AlertService.create_panic_alert(
            alert.tourist_id,
            alert.latitude,
            alert.longitude
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create panic alert"
            )
        
        return AlertResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating panic alert: {str(e)}"
        )

@router.post("/geofence", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_geofence_alert(alert: GeofenceAlertCreate):
    """Create a geofence alert"""
    try:
        result = AlertService.create_geofence_alert(
            alert.tourist_id,
            alert.latitude,
            alert.longitude,
            alert.zone_name
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create geofence alert"
            )
        
        return AlertResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating geofence alert: {str(e)}"
        )

@router.get("", response_model=List[AlertResponse])
def get_all_alerts():
    """Get all active alerts"""
    try:
        alerts = AlertService.get_all_alerts()
        return [AlertResponse(**alert) for alert in alerts]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving alerts: {str(e)}"
        )

@router.put("/{alert_id}/resolve", response_model=dict)
def resolve_alert(alert_id: int):
    """Mark alert as resolved"""
    try:
        success = AlertService.resolve_alert(alert_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return {"message": "Alert resolved successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving alert: {str(e)}"
        )