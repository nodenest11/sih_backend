from sqlalchemy import Column, BigInteger, ForeignKey, Date, JSON, Numeric, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class LocationHistory(Base):
    __tablename__ = "location_history"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tourist_id = Column(BigInteger, ForeignKey("tourists.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    location_data = Column(JSON, nullable=False)
    total_distance = Column(Numeric, nullable=True)
    unique_locations = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tourist = relationship("Tourist", back_populates="location_history")

    def __repr__(self):
        return f"<LocationHistory(id={self.id}, tourist_id={self.tourist_id}, date={self.date})>"