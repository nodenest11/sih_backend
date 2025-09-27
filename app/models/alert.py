from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, Numeric, Boolean, DateTime, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AlertType(str, enum.Enum):
    PANIC = "panic"
    GEOFENCE = "geofence"
    ANOMALY = "anomaly"
    TEMPORAL = "temporal"
    LOW_SAFETY_SCORE = "low_safety_score"
    SOS = "sos"
    MANUAL = "manual"


class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tourist_id = Column(BigInteger, ForeignKey("tourists.id"), nullable=False, index=True)
    type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.LOW, nullable=False)
    message = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Numeric(precision=10, scale=7), nullable=True)
    longitude = Column(Numeric(precision=10, scale=7), nullable=True)
    ai_confidence = Column(Numeric(precision=3, scale=2), nullable=True)
    auto_generated = Column(Boolean, default=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(String, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False)
    alert_metadata = Column(JSON, default={})

    # Relationships
    tourist = relationship("Tourist", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.type}, severity={self.severity}, status={self.status})>"