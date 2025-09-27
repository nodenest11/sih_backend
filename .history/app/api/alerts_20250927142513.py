from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
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
import json

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Alert Management"])


# 🚔 Function to send panic alerts to police dashboard
async def send_panic_to_police_dashboard(alert: Alert, tourist: Tourist, db: Session) -> dict:
    """
    Send panic alert to police dashboard API
    """
    try:
        # Prepare police dashboard data
        police_data = {
            "emergency_type": "TOURIST_PANIC_ALERT",
            "alert_id": alert.id,
            "severity": alert.severity.value,
            "timestamp": alert.timestamp.isoformat(),
            "location": {
                "latitude": float(alert.latitude) if alert.latitude else None,
                "longitude": float(alert.longitude) if alert.longitude else None,
                "coordinates": f"{alert.latitude}, {alert.longitude}" if alert.latitude and alert.longitude else "Unknown"
            },
            "tourist_info": {
                "id": tourist.id,
                "name": tourist.name,
                "contact": tourist.contact,
                "age": tourist.age,
                "nationality": tourist.nationality,
                "emergency_contact": tourist.emergency_contact,
                "safety_score": tourist.safety_score
            },
            "alert_details": {
                "message": alert.message,
                "description": alert.description,
                "type": alert.type.value,
                "auto_generated": alert.auto_generated
            },
            "response_required": True,
            "priority": "CRITICAL"
        }
        
        # Get police dashboard URL (you can configure this in environment variables)
        police_url = os.getenv("POLICE_DASHBOARD_URL", "http://police-api.example.com/emergency-alerts")
        police_api_key = os.getenv("POLICE_API_KEY", "")
        
        headers = {
            "Content-Type": "application/json",
            "X-Source": "Tourist-Safety-System",
            "X-Emergency-Type": "PANIC_ALERT"
        }
        
        if police_api_key:
            headers["Authorization"] = f"Bearer {police_api_key}"
        
        # Send to police dashboard with timeout
        timeout = httpx.Timeout(10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(police_url, json=police_data, headers=headers)
            
            if response.status_code == 200:
                # Mark alert as acknowledged by police system
                alert.acknowledged = True
                alert.acknowledged_by = "Police Dashboard"
                alert.acknowledged_at = datetime.utcnow()
                db.commit()
                
                return {"success": True, "message": "Alert sent to police dashboard"}
            else:
                return {"success": False, "message": f"Police API error: {response.status_code}"}
                
    except httpx.TimeoutException:
        return {"success": False, "message": "Police dashboard timeout"}
    except httpx.RequestError as e:
        return {"success": False, "message": f"Police dashboard connection error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unknown error: {str(e)}"}


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
        
        # 🚔 Automatically send panic alert to police dashboard
        try:
            police_result = await send_panic_to_police_dashboard(alert, tourist, db)
            if police_result["success"]:
                logger.critical(f"🚔 Panic alert {alert.id} sent to police dashboard successfully")
            else:
                logger.error(f"⚠️ Failed to send panic alert to police: {police_result['message']}")
        except Exception as e:
            logger.error(f"❌ Error sending panic alert to police dashboard: {e}")
            # Continue - alert is still created even if police notification fails
        
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


# 📊 New Endpoint: Get Alert Counts
@router.get("/counts", response_model=dict)
async def get_alert_counts(db: Session = Depends(get_db)):
    """
    Get count of alerts by different categories
    """
    try:
        # Total alerts
        total_alerts = db.query(func.count(Alert.id)).scalar()
        
        # Active alerts
        active_alerts = db.query(func.count(Alert.id)).filter(Alert.status == AlertStatus.ACTIVE).scalar()
        
        # Panic/SOS alerts
        panic_alerts = db.query(func.count(Alert.id)).filter(Alert.type.in_([AlertType.PANIC, AlertType.SOS])).scalar()
        
        # Critical alerts
        critical_alerts = db.query(func.count(Alert.id)).filter(Alert.severity == AlertSeverity.CRITICAL).scalar()
        
        # Today's alerts
        today = datetime.utcnow().date()
        today_alerts = db.query(func.count(Alert.id)).filter(
            func.date(Alert.timestamp) == today
        ).scalar()
        
        # Alerts by severity
        severity_counts = {}
        for severity in AlertSeverity:
            count = db.query(func.count(Alert.id)).filter(Alert.severity == severity).scalar()
            severity_counts[severity.value] = count
        
        # Alerts by type
        type_counts = {}
        for alert_type in AlertType:
            count = db.query(func.count(Alert.id)).filter(Alert.type == alert_type).scalar()
            type_counts[alert_type.value] = count
        
        # Alerts by status
        status_counts = {}
        for alert_status in AlertStatus:
            count = db.query(func.count(Alert.id)).filter(Alert.status == alert_status).scalar()
            status_counts[alert_status.value] = count
        
        # Police dashboard stats
        police_sent = db.query(func.count(Alert.id)).filter(
            Alert.acknowledged == True,
            Alert.acknowledged_by == "Police Dashboard"
        ).scalar()
        
        return {
            "summary": {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "panic_sos_alerts": panic_alerts,
                "critical_alerts": critical_alerts,
                "today_alerts": today_alerts,
                "police_notified": police_sent
            },
            "by_severity": severity_counts,
            "by_type": type_counts,
            "by_status": status_counts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting alert counts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alert counts"
        )


# 🚔 New Endpoint: Get Police Dashboard Status
@router.get("/police-status", response_model=dict)
async def get_police_dashboard_status(db: Session = Depends(get_db)):
    """
    Get status of alerts sent to police dashboard
    """
    try:
        # Alerts sent to police
        police_alerts = db.query(Alert).filter(
            Alert.acknowledged == True,
            Alert.acknowledged_by == "Police Dashboard"
        ).all()
        
        # Recent police alerts (last 24 hours)
        recent_time = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_police_alerts = db.query(Alert).filter(
            Alert.acknowledged == True,
            Alert.acknowledged_by == "Police Dashboard",
            Alert.acknowledged_at >= recent_time
        ).count()
        
        return {
            "police_dashboard_status": {
                "total_sent_to_police": len(police_alerts),
                "sent_today": recent_police_alerts,
                "last_sent": police_alerts[-1].acknowledged_at.isoformat() if police_alerts else None
            },
            "recent_police_alerts": [
                {
                    "alert_id": alert.id,
                    "tourist_id": alert.tourist_id,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "sent_at": alert.acknowledged_at.isoformat(),
                    "location": f"{alert.latitude}, {alert.longitude}" if alert.latitude else None
                }
                for alert in police_alerts[-10:]  # Last 10 alerts sent to police
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting police dashboard status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get police dashboard status"
        )


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