from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from app.database import Base
import enum


class RequestTypeEnum(str, enum.Enum):
    PLATFORM_ACCESS = "acceso_plataforma"
    TECHNICAL_SUPPORT = "soporte_tecnico"
    ACADEMIC = "academica"
    ADMINISTRATIVE = "administrativa"


class RequestStatusEnum(str, enum.Enum):
    RECEIVED = "recibida"
    PROCESSING = "en_proceso"
    COMPLETED = "completada"
    REJECTED = "rechazada"


class PriorityEnum(str, enum.Enum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"


class InstitutionalRequest(Base):
    __tablename__ = "institutional_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, nullable=False, index=True)
    external_id = Column(String(100), unique=True, nullable=False, index=True)
    requester_name = Column(String(255), nullable=False)
    requester_email = Column(String(255), nullable=False, index=True)
    institution_name = Column(String(255), nullable=False)
    request_type = Column(Enum(RequestTypeEnum), nullable=False, index=True)
    description = Column(Text, nullable=False)
    priority = Column(Enum(PriorityEnum), nullable=False, index=True, default=PriorityEnum.MEDIUM)
    status = Column(Enum(RequestStatusEnum), default=RequestStatusEnum.RECEIVED, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
