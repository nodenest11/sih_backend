from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Tourist
from schemas import TouristCreate, TouristResponse
from typing import List

router = APIRouter()

@router.post("/register", response_model=TouristResponse, status_code=status.HTTP_201_CREATED)
def register_tourist(tourist: TouristCreate, db: Session = Depends(get_db)):
    """Register a new tourist"""
    # Check if tourist with same contact already exists
    existing_tourist = db.query(Tourist).filter(Tourist.contact == tourist.contact).first()
    if existing_tourist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tourist with this contact number already exists"
        )
    
    # Create new tourist
    db_tourist = Tourist(
        name=tourist.name,
        contact=tourist.contact,
        trip_info=tourist.trip_info,
        emergency_contact=tourist.emergency_contact,
        safety_score=100  # Start with perfect safety score
    )
    
    db.add(db_tourist)
    db.commit()
    db.refresh(db_tourist)
    
    return db_tourist

@router.get("/{tourist_id}", response_model=TouristResponse)
def get_tourist(tourist_id: int, db: Session = Depends(get_db)):
    """Get tourist details by ID"""
    tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
    if not tourist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    return tourist

@router.get("/", response_model=List[TouristResponse])
def get_all_tourists(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tourists with pagination"""
    tourists = db.query(Tourist).offset(skip).limit(limit).all()
    return tourists

@router.put("/{tourist_id}/safety-score")
def update_safety_score(tourist_id: int, score_change: int, reason: str, db: Session = Depends(get_db)):
    """Update tourist safety score"""
    tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
    if not tourist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    
    # Update safety score (ensure it stays within 0-100 range)
    new_score = max(0, min(100, tourist.safety_score + score_change))
    tourist.safety_score = new_score
    
    db.commit()
    db.refresh(tourist)
    
    return {
        "tourist_id": tourist_id,
        "old_score": tourist.safety_score - score_change,
        "new_score": new_score,
        "change": score_change,
        "reason": reason
    }