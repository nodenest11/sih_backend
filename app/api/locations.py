from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Location, Tourist
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse, LocationSummary
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Location Management"])


# ✅ Required Endpoint: /sendLocation
@router.post("/sendLocation", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def send_location_endpoint(
    location_data: LocationUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send tourist location update and trigger AI safety assessment.
    Required endpoint: /sendLocation
    """
    try:
        # Verify tourist exists
        tourist = db.query(Tourist).filter(Tourist.id == location_data.tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        if not tourist.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tourist is inactive"
            )
        
        # Create location record
        location_dict = location_data.dict()
        if location_dict.get('timestamp') is None:
            location_dict['timestamp'] = datetime.utcnow()
            
        db_location = Location(**location_dict)
        db.add(db_location)
        
        # Update tourist's last location update
        tourist.last_location_update = datetime.utcnow()
        
        db.commit()
        db.refresh(db_location)
        
        # 🤖 Trigger AI Assessment in background
        try:
            from app.api.ai_assessment import get_ai_engine
            engine = get_ai_engine()
            background_tasks.add_task(
                engine.assess_tourist_safety,
                tourist_id=location_data.tourist_id,
                location_id=db_location.id
            )
            logger.info(f"AI assessment triggered for tourist {location_data.tourist_id}")
        except Exception as e:
            logger.warning(f"Failed to trigger AI assessment: {e}")
        
        logger.info(f"Location updated for tourist {location_data.tourist_id}: ({location_data.latitude}, {location_data.longitude})")
        return db_location
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update location"
        )


# Legacy endpoint for backward compatibility  
@router.post("/update", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def update_location(
    location_data: LocationUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update tourist location (legacy endpoint)"""
    return await send_location_endpoint(location_data, background_tasks, db)


@router.get("/all", response_model=List[LocationSummary])
async def get_all_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get latest location of all active tourists.
    """
    try:
        # Get the latest location for each active tourist
        subquery = db.query(
            Location.tourist_id,
            desc(Location.timestamp).label('max_timestamp')
        ).group_by(Location.tourist_id).subquery()
        
        locations = db.query(
            Location,
            Tourist.name.label('tourist_name'),
            Tourist.safety_score
        ).join(
            Tourist, Location.tourist_id == Tourist.id
        ).join(
            subquery, 
            (Location.tourist_id == subquery.c.tourist_id) & 
            (Location.timestamp == subquery.c.max_timestamp)
        ).filter(
            Tourist.is_active == True
        ).offset(max(0, skip)).limit(min(max(1, limit), 1000)).all()
        
        # Format response
        result = []
        for location, tourist_name, safety_score in locations:
            result.append(LocationSummary(
                tourist_id=location.tourist_id,
                tourist_name=tourist_name,
                latitude=float(location.latitude),
                longitude=float(location.longitude),
                timestamp=location.timestamp,
                safety_score=safety_score
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching all locations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch locations"
        )


@router.get("/tourist/{tourist_id}", response_model=List[LocationResponse])
async def get_tourist_locations(
    tourist_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get location history for a specific tourist.
    """
    try:
        # Verify tourist exists
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Get locations ordered by most recent
        locations = db.query(Location).filter(
            Location.tourist_id == tourist_id
        ).order_by(
            desc(Location.timestamp)
        ).limit(limit).all()
        
        return locations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching locations for tourist {tourist_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tourist locations"
        )


@router.get("/latest/{tourist_id}", response_model=LocationResponse)
async def get_latest_location(
    tourist_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the latest location for a specific tourist.
    """
    try:
        # Verify tourist exists
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Get the latest location
        location = db.query(Location).filter(
            Location.tourist_id == tourist_id
        ).order_by(
            desc(Location.timestamp)
        ).first()
        
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No location data found for this tourist"
            )
        
        return location
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest location for tourist {tourist_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest location"
        )