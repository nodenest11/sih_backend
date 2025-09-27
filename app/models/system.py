from sqlalchemy import Column, BigInteger, String, Integer, Numeric, Text, JSON, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class MetricType(str, enum.Enum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    ACTIVE_TOURISTS = "active_tourists"
    REQUESTS_PER_MINUTE = "requests_per_minute"
    ERROR_RATE = "error_rate"


class APILog(Base):
    __tablename__ = "api_logs"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Numeric, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)  # Using String instead of inet for simplicity
    request_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<APILog(id={self.id}, endpoint='{self.endpoint}', method='{self.method}', status={self.status_code})>"


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    metric_type = Column(Enum(MetricType), nullable=False)
    value = Column(Numeric, nullable=False)
    unit = Column(String, nullable=True)
    metric_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SystemMetric(id={self.id}, type={self.metric_type}, value={self.value})>"