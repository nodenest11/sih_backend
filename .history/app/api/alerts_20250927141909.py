from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Alert, Tourist, AlertType, AlertSeverity, AlertStatus
from app.schemas.alert import (
    AlertCreate, PanicAlertCreate, GeofenceAlertCreate, 
    AlertUpdate, AlertResponse, AlertSummary
)
import logging
import httpx
import os

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Alert Management"])


# Internal helper function for sending alerts to police
async def send_panic_alert_to_police_internal(alert_id: int, db: Session) -> dict:
    """
    Internal function to send panic alerts to police dashboard.
    Used by other endpoints to automatically forward critical alerts.
    """
    try:
        # Get the alert
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return {"success": False, "message": "Alert not found"}
        
        # Check if it's a panic/SOS alert
        if alert.type not in [AlertType.PANIC, AlertType.SOS]:
            return {"success": False, "message": "Only panic/SOS alerts can be sent to police"}
        
        # Get tourist information
        tourist = db.query(Tourist).filter(Tourist.id == alert.tourist_id).first()
        if not tourist:
            return {"success": False, "message": "Tourist not found"}
        
        # Prepare data for police dashboard
        police_alert_data = {
            "emergency_type": "TOURIST_SOS_PANIC",
            "alert_id": alert.id,
            "severity": alert.severity.value,
            "timestamp": alert.timestamp.isoformat(),
            "location": {
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "address": f"Lat: {alert.latitude}, Lon: {alert.longitude}"
            },
            "tourist_info": {
                "id": tourist.id,
                "name": tourist.name,
                "contact": tourist.contact,
                "age": tourist.age,
                "nationality": tourist.nationality,
                "emergency_contact": tourist.emergency_contact
            },
            "alert_details": {
                "message": alert.message,
                "description": alert.description,
                "ai_confidence": alert.ai_confidence,
                "safety_score": tourist.safety_score
            },
            "response_required": True,
            "priority": "CRITICAL" if alert.severity == AlertSeverity.CRITICAL else "HIGH"
        }
        
        # Get police dashboard URL from environment variables
        police_dashboard_url = os.getenv("POLICE_DASHBOARD_URL", "http://police-dashboard-api.gov.in/api/emergency-alerts")
        police_api_key = os.getenv("POLICE_API_KEY", "")
        
        # Headers for police API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {police_api_key}" if police_api_key else "",
            "X-Source-System": "Tourist-Safety-System",
            "X-Alert-Priority": "CRITICAL"
        }
        
        # Send to police dashboard
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                police_dashboard_url,
                json=police_alert_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "Alert sent to police dashboard"}
            else:
                return {"success": False, "message": f"Police API error: {response.status_code}"}
                
    except Exception as e:
        logger.error(f"Error in police alert internal function: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}


# ✅ Required Endpoint: /pressSOS
@router.post("/pressSOS", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def press_sos_endpoint(
    panic_data: PanicAlertCreate,
    db: Session = Depends(get_db)
):
    """
    Create an emergency SOS alert for a tourist.
    Required endpoint: /pressSOS
    """
    try:
        # Verify tourist exists
        tourist = db.query(Tourist).filter(Tourist.id == panic_data.tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Create SOS alert with CRITICAL severity
        alert = Alert(
            tourist_id=panic_data.tourist_id,
            type=AlertType.PANIC,  # SOS is treated as panic
            severity=AlertSeverity.CRITICAL,
            message=f"🆘 EMERGENCY SOS: {panic_data.message}",
            latitude=panic_data.latitude,
            longitude=panic_data.longitude,
            auto_generated=False,
            status=AlertStatus.ACTIVE
        )
        
        db.add(alert)
        
        # Update tourist safety score (SOS = -40, minimum score 0)
        tourist.safety_score = max(0, tourist.safety_score - 40)
        
        db.commit()
        db.refresh(alert)
        
        logger.critical(f"🆘 SOS ALERT created for tourist {panic_data.tourist_id}: {panic_data.message}")
        
        # Automatically send critical SOS alerts to police dashboard
        try:
            police_result = await send_panic_alert_to_police_internal(alert.id, db)
            if police_result.get("success"):
                logger.critical(f"🚔 SOS Alert {alert.id} automatically forwarded to police dashboard")
        except Exception as e:
            logger.error(f"Failed to automatically send SOS alert to police: {e}")
            # Continue execution - alert is still created even if police notification fails
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating SOS alert: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create SOS alert"
        )


@router.post("/sendToPoliceDashboard", response_model=dict, status_code=status.HTTP_200_OK)
async def send_panic_alert_to_police(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Send panic/SOS alert to police dashboard via API.
    This endpoint forwards critical alerts to law enforcement systems.
    """
    try:
        # Get the alert
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Check if it's a panic/SOS alert
        if alert.type not in [AlertType.PANIC, AlertType.SOS]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only panic/SOS alerts can be sent to police dashboard"
            )
        
        # Get tourist information
        tourist = db.query(Tourist).filter(Tourist.id == alert.tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Prepare data for police dashboard
        police_alert_data = {
            "emergency_type": "TOURIST_SOS_PANIC",
            "alert_id": alert.id,
            "severity": alert.severity.value,
            "timestamp": alert.timestamp.isoformat(),
            "location": {
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "address": f"Lat: {alert.latitude}, Lon: {alert.longitude}"  # Could be enhanced with reverse geocoding
            },
            "tourist_info": {
                "id": tourist.id,
                "name": tourist.name,
                "contact": tourist.contact,
                "age": tourist.age,
                "nationality": tourist.nationality,
                "emergency_contact": tourist.emergency_contact
            },
            "alert_details": {
                "message": alert.message,
                "description": alert.description,
                "ai_confidence": alert.ai_confidence,
                "safety_score": tourist.safety_score
            },
            "response_required": True,
            "priority": "CRITICAL" if alert.severity == AlertSeverity.CRITICAL else "HIGH"
        }
        
        # Get police dashboard URL from environment variables
        police_dashboard_url = os.getenv("POLICE_DASHBOARD_URL", "http://police-dashboard-api.gov.in/api/emergency-alerts")
        police_api_key = os.getenv("POLICE_API_KEY", "")
        
        # Headers for police API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {police_api_key}" if police_api_key else "",
            "X-Source-System": "Tourist-Safety-System",
            "X-Alert-Priority": "CRITICAL"
        }
        
        # Send to police dashboard
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    police_dashboard_url,
                    json=police_alert_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    # Update alert to mark it as sent to police
                    alert.acknowledged = True
                    alert.acknowledged_by = "Police Dashboard System"
                    alert.acknowledged_at = datetime.utcnow()
                    
                    db.commit()
                    
                    logger.critical(f"🚔 PANIC ALERT {alert_id} successfully sent to police dashboard")
                    
                    return {
                        "success": True,
                        "message": "Alert successfully sent to police dashboard",
                        "alert_id": alert_id,
                        "police_response_status": response.status_code,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    logger.error(f"Police dashboard API returned status {response.status_code}: {response.text}")
                    return {
                        "success": False,
                        "message": f"Police dashboard API error: {response.status_code}",
                        "alert_id": alert_id,
                        "error_details": response.text,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout sending alert {alert_id} to police dashboard")
            return {
                "success": False,
                "message": "Timeout connecting to police dashboard",
                "alert_id": alert_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        except httpx.RequestError as e:
            logger.error(f"Request error sending alert {alert_id} to police: {e}")
            return {
                "success": False,
                "message": f"Connection error to police dashboard: {str(e)}",
                "alert_id": alert_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending alert {alert_id} to police dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send alert to police dashboard: {str(e)}"
        )
        
        db.commit()
        db.refresh(alert)
        
        logger.warning(f"PANIC ALERT created for tourist {panic_data.tourist_id} at {panic_data.latitude}, {panic_data.longitude}")
        
        # TODO: Trigger immediate emergency response
        # This is where we would notify emergency services, family, etc.
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating panic alert: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create panic alert"
        )


@router.post("/geofence", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_geofence_alert(
    geofence_data: GeofenceAlertCreate,
    db: Session = Depends(get_db)
):
    """
    Create a geofence alert when tourist enters restricted area.
    """
    try:
        # Verify tourist exists
        tourist = db.query(Tourist).filter(Tourist.id == geofence_data.tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Create geofence alert
        message = geofence_data.message or f"Tourist entered restricted zone: {geofence_data.zone_name}"
        
        alert = Alert(
            tourist_id=geofence_data.tourist_id,
            type=AlertType.GEOFENCE,
            severity=AlertSeverity.HIGH,
            message=message,
            description=f"Tourist entered restricted zone: {geofence_data.zone_name}",
            latitude=geofence_data.latitude,
            longitude=geofence_data.longitude,
            auto_generated=True,
            status=AlertStatus.ACTIVE
        )
        
        db.add(alert)
        
        # Update tourist safety score (risky zone = -20)
        tourist.safety_score = max(0, tourist.safety_score - 20)
        
        db.commit()
        db.refresh(alert)
        
        logger.warning(f"GEOFENCE ALERT created for tourist {geofence_data.tourist_id} - entered {geofence_data.zone_name}")
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating geofence alert: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create geofence alert"
        )


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db)
):
    """
    Create a generic alert.
    """
    try:
        # Verify tourist exists
        tourist = db.query(Tourist).filter(Tourist.id == alert_data.tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Create alert
        alert = Alert(**alert_data.dict())
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alert created: {alert.type} for tourist {alert_data.tourist_id}")
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert"
        )


# ✅ Required Endpoint: /getAlerts
@router.get("/getAlerts", response_model=List[AlertSummary])
async def get_alerts_endpoint(
    status: Optional[AlertStatus] = AlertStatus.ACTIVE,
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get alerts with optional filtering.
    Required endpoint: /getAlerts
    """
    try:
        query = db.query(Alert, Tourist.name.label('tourist_name')).join(
            Tourist, Alert.tourist_id == Tourist.id
        )
        
        # Apply filters
        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)
        if alert_type:
            query = query.filter(Alert.type == alert_type)
        
        # Order by most recent first
        query = query.order_by(desc(Alert.timestamp))
        
        # Apply pagination
        alerts_data = query.offset(skip).limit(limit).all()
        
        # Transform to response format
        alerts = []
        for alert, tourist_name in alerts_data:
            alert_dict = {
                "id": alert.id,
                "tourist_id": alert.tourist_id,
                "tourist_name": tourist_name,
                "type": alert.type,
                "severity": alert.severity,
                "message": alert.message,
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "timestamp": alert.timestamp,
                "status": alert.status,
                "acknowledged": alert.acknowledged,
                "resolved_at": alert.resolved_at
            }
            alerts.append(alert_dict)
        
        logger.info(f"Retrieved {len(alerts)} alerts")
        return alerts
        
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts"
        )


# Legacy endpoint for backward compatibility
@router.get("/", response_model=List[AlertSummary])
async def get_alerts(
    status: Optional[AlertStatus] = AlertStatus.ACTIVE,
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get alerts (legacy endpoint)"""
    return await get_alerts_endpoint(status, severity, alert_type, skip, limit, db)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific alert by ID.
    """
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alert {alert_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch alert"
        )


@router.put("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: int,
    resolution_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    Resolve an alert.
    """
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Update alert status
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        
        if resolution_data.resolved_by:
            alert.resolved_by = resolution_data.resolved_by
        if resolution_data.resolution_notes:
            alert.resolution_notes = resolution_data.resolution_notes
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alert {alert_id} resolved by {resolution_data.resolved_by}")
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert {alert_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert"
        )


@router.put("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: int,
    acknowledgment_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert.
    """
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Update acknowledgment status
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.status = AlertStatus.ACKNOWLEDGED
        
        if acknowledgment_data.acknowledged_by:
            alert.acknowledged_by = acknowledgment_data.acknowledged_by
        
        db.commit()
        db.refresh(alert)
        
        logger.info(f"Alert {alert_id} acknowledged by {acknowledgment_data.acknowledged_by}")
        
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert {alert_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert"
        )