from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from app.database import Base
import enum


class RequestStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstitutionalRequest(Base):
    __tablename__ = "institutional_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    requester_name = Column(String(255), nullable=False)
    requester_email = Column(String(255), nullable=False, index=True)
    institution_name = Column(String(255), nullable=False)
    request_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(RequestStatusEnum), default=RequestStatusEnum.PENDING, nullable=False)
    external_reference_id = Column(String(100), nullable=True, unique=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    class Config:
        from_attributes = True
