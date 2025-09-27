from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Tourist
from app.schemas.tourist import TouristCreate, TouristResponse, TouristSummary, TouristUpdate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Tourist Management"])


# ✅ Required Endpoint: /registerTourist
@router.post("/registerTourist", response_model=TouristResponse, status_code=status.HTTP_201_CREATED)
async def register_tourist_endpoint(
    tourist_data: TouristCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new tourist in the system.
    Required endpoint: /registerTourist
    """
    try:
        # Check if contact already exists
        existing_tourist = db.query(Tourist).filter(Tourist.contact == tourist_data.contact).first()
        if existing_tourist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tourist with this contact number already exists"
            )
        
        # Create new tourist with safety score 100 (default)
        db_tourist = Tourist(**tourist_data.dict())
        db.add(db_tourist)
        db.commit()
        db.refresh(db_tourist)
        
        logger.info(f"New tourist registered: {db_tourist.id} - {db_tourist.name}")
        return db_tourist
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering tourist: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register tourist"
        )


# Legacy endpoint for backward compatibility  
@router.post("/register", response_model=TouristResponse, status_code=status.HTTP_201_CREATED)
async def register_tourist(
    tourist_data: TouristCreate,
    db: Session = Depends(get_db)
):
    """Register a new tourist (legacy endpoint)"""
    return await register_tourist_endpoint(tourist_data, db)


@router.get("/{tourist_id}", response_model=TouristResponse)
async def get_tourist(
    tourist_id: int,
    db: Session = Depends(get_db)
):
    """
    Get tourist details by ID including safety score and trip info.
    """
    try:
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        return tourist
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tourist {tourist_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tourist details"
        )


@router.get("/", response_model=List[TouristSummary])
async def list_tourists(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all tourists with optional filtering.
    """
    try:
        query = db.query(Tourist)
        
        if active_only:
            query = query.filter(Tourist.is_active == True)
        
        tourists = query.offset(skip).limit(limit).all()
        return tourists
        
    except Exception as e:
        logger.error(f"Error listing tourists: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tourists list"
        )


@router.put("/{tourist_id}", response_model=TouristResponse)
async def update_tourist(
    tourist_id: int,
    tourist_update: TouristUpdate,
    db: Session = Depends(get_db)
):
    """
    Update tourist information.
    """
    try:
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        # Update only provided fields
        update_data = tourist_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tourist, field, value)
        
        db.commit()
        db.refresh(tourist)
        
        logger.info(f"Tourist updated: {tourist_id}")
        return tourist
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tourist {tourist_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tourist"
        )


@router.delete("/{tourist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_tourist(
    tourist_id: int,
    db: Session = Depends(get_db)
):
    """
    Deactivate a tourist (soft delete).
    """
    try:
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tourist not found"
            )
        
        tourist.is_active = False
        db.commit()
        
        logger.info(f"Tourist deactivated: {tourist_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating tourist {tourist_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate tourist"
        )