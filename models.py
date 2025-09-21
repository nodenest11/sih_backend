from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class AlertType(enum.Enum):
    panic = "panic"
    geofence = "geofence"

class AlertStatus(enum.Enum):
    active = "active"
    resolved = "resolved"

class Tourist(Base):
    __tablename__ = "tourists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact = Column(String(20), nullable=False)
    trip_info = Column(Text)
    emergency_contact = Column(String(20), nullable=False)
    safety_score = Column(Integer, default=100)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    locations = relationship("Location", back_populates="tourist")
    alerts = relationship("Alert", back_populates="tourist")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    tourist_id = Column(Integer, ForeignKey("tourists.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tourist = relationship("Tourist", back_populates="locations")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    tourist_id = Column(Integer, ForeignKey("tourists.id"), nullable=False)
    type = Column(Enum(AlertType), nullable=False)
    message = Column(Text, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(AlertStatus), default=AlertStatus.active)
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    tourist = relationship("Tourist", back_populates="alerts")

class RestrictedZone(Base):
    __tablename__ = "restricted_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    # Store polygon coordinates as JSON string
    polygon_coordinates = Column(Text, nullable=False)
    risk_level = Column(Integer, default=5)  # 1-10 scale
    created_at = Column(DateTime(timezone=True), server_default=func.now())