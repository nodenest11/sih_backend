from sqlalchemy.orm import Session
from models import Tourist, Alert, Location, AlertType
from datetime import datetime, timedelta
import json

class SafetyScoreService:
    """Service for calculating and updating tourist safety scores"""
    
    # Score changes based on events
    SCORE_CHANGES = {
        "panic_alert": -40,
        "geofence_violation": -20,
        "safe_duration_1hr": +10,
        "safe_check_in": +5,
        "emergency_contact_update": +2
    }
    
    @staticmethod
    def update_score_for_panic(tourist_id: int, db: Session) -> int:
        """Update safety score when panic alert is triggered"""
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            return 0
        
        old_score = tourist.safety_score
        new_score = max(0, old_score + SafetyScoreService.SCORE_CHANGES["panic_alert"])
        tourist.safety_score = new_score
        
        db.commit()
        return new_score - old_score
    
    @staticmethod
    def update_score_for_geofence(tourist_id: int, db: Session) -> int:
        """Update safety score when geofence violation occurs"""
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            return 0
        
        old_score = tourist.safety_score
        new_score = max(0, old_score + SafetyScoreService.SCORE_CHANGES["geofence_violation"])
        tourist.safety_score = new_score
        
        db.commit()
        return new_score - old_score
    
    @staticmethod
    def check_and_update_safe_duration(tourist_id: int, db: Session) -> int:
        """Check if tourist has been safe for 1 hour and update score"""
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            return 0
        
        # Check for any active alerts in the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_alerts = (
            db.query(Alert)
            .filter(
                Alert.tourist_id == tourist_id,
                Alert.timestamp >= one_hour_ago
            )
            .count()
        )
        
        # If no alerts in the last hour, award safe duration points
        if recent_alerts == 0:
            old_score = tourist.safety_score
            new_score = min(100, old_score + SafetyScoreService.SCORE_CHANGES["safe_duration_1hr"])
            tourist.safety_score = new_score
            
            db.commit()
            return new_score - old_score
        
        return 0
    
    @staticmethod
    def update_score_for_safe_checkin(tourist_id: int, db: Session) -> int:
        """Update safety score for regular location check-in"""
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            return 0
        
        # Award points for regular check-ins (max once per 30 minutes)
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)
        recent_locations = (
            db.query(Location)
            .filter(
                Location.tourist_id == tourist_id,
                Location.timestamp >= thirty_minutes_ago
            )
            .count()
        )
        
        # Only award points if this is the first check-in in 30 minutes
        if recent_locations <= 1:
            old_score = tourist.safety_score
            new_score = min(100, old_score + SafetyScoreService.SCORE_CHANGES["safe_check_in"])
            tourist.safety_score = new_score
            
            db.commit()
            return new_score - old_score
        
        return 0
    
    @staticmethod
    def calculate_risk_assessment(tourist_id: int, db: Session) -> dict:
        """Calculate comprehensive risk assessment for a tourist"""
        tourist = db.query(Tourist).filter(Tourist.id == tourist_id).first()
        if not tourist:
            return {}
        
        # Get recent alerts (last 24 hours)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        recent_alerts = (
            db.query(Alert)
            .filter(
                Alert.tourist_id == tourist_id,
                Alert.timestamp >= twenty_four_hours_ago
            )
            .all()
        )
        
        # Get latest location
        latest_location = (
            db.query(Location)
            .filter(Location.tourist_id == tourist_id)
            .order_by(Location.timestamp.desc())
            .first()
        )
        
        # Calculate risk level
        risk_level = "low"
        if tourist.safety_score < 30:
            risk_level = "critical"
        elif tourist.safety_score < 50:
            risk_level = "high"
        elif tourist.safety_score < 70:
            risk_level = "medium"
        
        # Count alert types
        panic_alerts = len([a for a in recent_alerts if a.type == AlertType.panic])
        geofence_alerts = len([a for a in recent_alerts if a.type == AlertType.geofence])
        
        return {
            "tourist_id": tourist_id,
            "tourist_name": tourist.name,
            "safety_score": tourist.safety_score,
            "risk_level": risk_level,
            "recent_alerts_24h": len(recent_alerts),
            "panic_alerts_24h": panic_alerts,
            "geofence_alerts_24h": geofence_alerts,
            "latest_location": {
                "latitude": latest_location.latitude if latest_location else None,
                "longitude": latest_location.longitude if latest_location else None,
                "timestamp": latest_location.timestamp if latest_location else None
            },
            "recommendations": SafetyScoreService._get_recommendations(tourist.safety_score, recent_alerts)
        }
    
    @staticmethod
    def _get_recommendations(safety_score: int, recent_alerts: list) -> list:
        """Get safety recommendations based on score and recent activity"""
        recommendations = []
        
        if safety_score < 30:
            recommendations.extend([
                "Immediate assistance may be required",
                "Contact emergency services if needed",
                "Verify tourist's current status"
            ])
        elif safety_score < 50:
            recommendations.extend([
                "Monitor tourist closely",
                "Consider reaching out to check status",
                "Review recent travel patterns"
            ])
        elif safety_score < 70:
            recommendations.extend([
                "Encourage safe travel practices",
                "Remind about restricted areas",
                "Regular check-ins recommended"
            ])
        else:
            recommendations.append("Tourist appears to be traveling safely")
        
        if len(recent_alerts) > 3:
            recommendations.append("High alert frequency - investigate patterns")
        
        return recommendations