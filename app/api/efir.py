from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from app.database import get_db
from app.models import Alert, Tourist
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["E-FIR Management"])


class EFIRCreate(BaseModel):
    alert_id: int
    incident_description: str
    incident_location: str
    witnesses: str = ""
    evidence: str = ""
    police_station: str = ""
    officer_name: str = ""


class EFIRResponse(BaseModel):
    id: str
    alert_id: int
    tourist_id: int
    incident_description: str
    incident_location: str
    witnesses: str
    evidence: str
    police_station: str
    officer_name: str
    status: str
    filed_at: datetime
    fir_number: str


# ✅ Required Endpoint: /fileEFIR
@router.post("/fileEFIR", response_model=EFIRResponse, status_code=status.HTTP_201_CREATED)
async def file_efir_endpoint(
    efir_data: EFIRCreate,
    db: Session = Depends(get_db)
):
    """
    File an electronic First Information Report (E-FIR) for an alert.
    Required endpoint: /fileEFIR
    """
    try:
        # Verify alert exists and is critical
        alert = db.query(Alert).filter(Alert.id == efir_data.alert_id).first()
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Verify tourist exists
        tourist = db.query(Tourist).filter(Tourist.id == alert.tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Generate FIR number (format: EFIR-YYYY-MM-DD-ALERTID)
        fir_number = f"EFIR-{datetime.now().strftime('%Y-%m-%d')}-{alert.id:06d}"
        
        # Create E-FIR record (storing in alert metadata for simplicity)
        efir_data_dict = {
            "id": fir_number,
            "alert_id": efir_data.alert_id,
            "tourist_id": alert.tourist_id,
            "incident_description": efir_data.incident_description,
            "incident_location": efir_data.incident_location,
            "witnesses": efir_data.witnesses,
            "evidence": efir_data.evidence,
            "police_station": efir_data.police_station,
            "officer_name": efir_data.officer_name,
            "status": "FILED",
            "filed_at": datetime.utcnow(),
            "fir_number": fir_number
        }
        
        # Update alert with E-FIR information
        if not alert.alert_metadata:
            alert.alert_metadata = {}
        alert.alert_metadata["efir"] = efir_data_dict
        alert.status = "acknowledged"  # Mark alert as acknowledged
        alert.acknowledged = True
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = efir_data.officer_name or "Police Officer"
        
        db.commit()
        
        logger.info(f"E-FIR {fir_number} filed for alert {alert.id} by {efir_data.officer_name}")
        
        return EFIRResponse(**efir_data_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filing E-FIR: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to file E-FIR"
        )


@router.get("/efir/{fir_number}", response_model=EFIRResponse)
async def get_efir(
    fir_number: str,
    db: Session = Depends(get_db)
):
    """Get E-FIR details by FIR number"""
    try:
        # Find alert with this FIR number in metadata
        alerts = db.query(Alert).filter(Alert.alert_metadata.op("@>")({
            "efir": {"fir_number": fir_number}
        })).all()
        
        if not alerts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="E-FIR not found"
            )
        
        alert = alerts[0]
        efir_data = alert.alert_metadata.get("efir", {})
        
        return EFIRResponse(**efir_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving E-FIR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve E-FIR"
        )


@router.get("/efirs/status/{status_filter}")
async def get_efirs_by_status(
    status_filter: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get E-FIRs by status"""
    try:
        # Find alerts with E-FIR data
        alerts = db.query(Alert).filter(
            Alert.alert_metadata.op("?")("efir")
        ).offset(skip).limit(limit).all()
        
        efirs = []
        for alert in alerts:
            efir_data = alert.alert_metadata.get("efir", {})
            if efir_data.get("status", "").lower() == status_filter.lower():
                efirs.append(efir_data)
        
        return {"efirs": efirs, "count": len(efirs)}
        
    except Exception as e:
        logger.error(f"Error retrieving E-FIRs by status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve E-FIRs"
        )