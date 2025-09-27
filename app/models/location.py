from sqlalchemy import Column, BigInteger, ForeignKey, Numeric, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tourist_id = Column(BigInteger, ForeignKey("tourists.id"), nullable=False, index=True)
    latitude = Column(Numeric(precision=10, scale=7), nullable=False)
    longitude = Column(Numeric(precision=10, scale=7), nullable=False)
    altitude = Column(Numeric, nullable=True)
    accuracy = Column(Numeric, nullable=True)
    speed = Column(Numeric, nullable=True)
    heading = Column(Numeric, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tourist = relationship("Tourist", back_populates="locations")
    ai_assessments = relationship("AIAssessment", back_populates="location")

    def __repr__(self):
        return f"<Location(id={self.id}, tourist_id={self.tourist_id}, lat={self.latitude}, lon={self.longitude})>"