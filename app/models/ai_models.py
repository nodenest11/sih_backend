from sqlalchemy import Column, BigInteger, ForeignKey, Integer, String, Numeric, Text, JSON, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AISeverity(str, enum.Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AIAssessment(Base):
    __tablename__ = "ai_assessments"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tourist_id = Column(BigInteger, ForeignKey("tourists.id"), nullable=False, index=True)
    location_id = Column(BigInteger, ForeignKey("locations.id"), nullable=False, index=True)
    safety_score = Column(Integer, nullable=False)  # 0-100
    severity = Column(Enum(AISeverity), nullable=False)
    geofence_alert = Column(Boolean, default=False)
    anomaly_score = Column(Numeric(precision=3, scale=2), nullable=True)  # 0-1
    temporal_risk_score = Column(Numeric(precision=3, scale=2), nullable=True)  # 0-1
    supervised_prediction = Column(Numeric(precision=3, scale=2), nullable=True)  # 0-1
    confidence_level = Column(Numeric(precision=3, scale=2), nullable=False)  # 0-1
    recommended_action = Column(String, nullable=True)
    alert_message = Column(Text, nullable=True)
    model_versions = Column(JSON, default={})
    processing_time_ms = Column(Numeric, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tourist = relationship("Tourist", back_populates="ai_assessments")
    location = relationship("Location", back_populates="ai_assessments")
    ai_predictions = relationship("AIModelPrediction", back_populates="assessment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AIAssessment(id={self.id}, safety_score={self.safety_score}, severity={self.severity})>"


class AIModelName(str, enum.Enum):
    GEOFENCE = "geofence"
    ISOLATION_FOREST = "isolation_forest"
    TEMPORAL_AUTOENCODER = "temporal_autoencoder"
    LIGHTGBM_CLASSIFIER = "lightgbm_classifier"


class AIModelPrediction(Base):
    __tablename__ = "ai_model_predictions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    assessment_id = Column(BigInteger, ForeignKey("ai_assessments.id"), nullable=False, index=True)
    model_name = Column(Enum(AIModelName), nullable=False)
    prediction_value = Column(Numeric(precision=3, scale=2), nullable=False)  # 0-1
    confidence = Column(Numeric(precision=3, scale=2), nullable=False)  # 0-1
    processing_time_ms = Column(Numeric, nullable=True)
    model_version = Column(String, nullable=True)
    model_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    assessment = relationship("AIAssessment", back_populates="ai_predictions")

    def __repr__(self):
        return f"<AIModelPrediction(id={self.id}, model={self.model_name}, prediction={self.prediction_value})>"