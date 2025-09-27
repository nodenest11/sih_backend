from sqlalchemy import Column, BigInteger, String, Text, JSON, Integer, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class ZoneType(str, enum.Enum):
    TOURIST_AREA = "tourist_area"
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    TRANSPORT_HUB = "transport_hub"
    HOSPITAL = "hospital"
    POLICE_STATION = "police_station"


class SafeZone(Base):
    __tablename__ = "safe_zones"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    zone_type = Column(Enum(ZoneType), nullable=False)
    coordinates = Column(JSON, nullable=False)  # GeoJSON polygon
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, default="India")
    safety_rating = Column(Integer, default=5)  # 1-5 scale
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SafeZone(id={self.id}, name='{self.name}', type={self.zone_type})>"


class RestrictedZoneType(str, enum.Enum):
    RESTRICTED = "restricted"
    MILITARY = "military"
    PRIVATE = "private"
    DANGEROUS = "dangerous"
    CONSTRUCTION = "construction"
    NATURAL_HAZARD = "natural_hazard"


class RestrictedZone(Base):
    __tablename__ = "restricted_zones"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    zone_type = Column(Enum(RestrictedZoneType), nullable=False)
    coordinates = Column(JSON, nullable=False)  # GeoJSON polygon
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, default="India")
    danger_level = Column(Integer, default=3)  # 1-5 scale
    buffer_zone_meters = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<RestrictedZone(id={self.id}, name='{self.name}', type={self.zone_type})>"