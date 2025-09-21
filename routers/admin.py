from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from services import SafetyScoreService
from seed_data import seed_database
import threading

router = APIRouter()

@router.get("/{tourist_id}/risk-assessment")
def get_risk_assessment(tourist_id: int, db: Session = Depends(get_db)):
    """Get comprehensive risk assessment for a tourist"""
    assessment = SafetyScoreService.calculate_risk_assessment(tourist_id, db)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tourist not found"
        )
    return assessment

@router.post("/{tourist_id}/safe-checkin")
def safe_checkin(tourist_id: int, db: Session = Depends(get_db)):
    """Award points for safe check-in"""
    score_change = SafetyScoreService.update_score_for_safe_checkin(tourist_id, db)
    if score_change == 0:
        return {
            "message": "No score change - recent check-in already recorded",
            "tourist_id": tourist_id,
            "score_change": 0
        }
    
    return {
        "message": "Safe check-in recorded",
        "tourist_id": tourist_id,
        "score_change": score_change
    }

@router.post("/{tourist_id}/check-safe-duration")
def check_safe_duration(tourist_id: int, db: Session = Depends(get_db)):
    """Check and update score for safe duration"""
    score_change = SafetyScoreService.check_and_update_safe_duration(tourist_id, db)
    
    return {
        "message": "Safe duration check completed" if score_change > 0 else "No safe duration bonus - recent alerts found",
        "tourist_id": tourist_id,
        "score_change": score_change
    }

@router.post("/seed-database")
def initialize_sample_data():
    """Initialize database with sample data (run once)"""
    try:
        # Run seeding in a separate thread to avoid blocking
        def run_seed():
            seed_database()
        
        thread = threading.Thread(target=run_seed)
        thread.start()
        
        return {
            "message": "Database seeding initiated. This may take a few moments.",
            "status": "in_progress"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating database seeding: {str(e)}"
        )