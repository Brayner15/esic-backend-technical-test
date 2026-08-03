from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class RequestTypeEnum(str, Enum):
    PLATFORM_ACCESS = "acceso_plataforma"
    TECHNICAL_SUPPORT = "soporte_tecnico"
    ACADEMIC = "academica"
    ADMINISTRATIVE = "administrativa"


class RequestStatusEnum(str, Enum):
    RECEIVED = "recibida"
    PROCESSING = "en_proceso"
    COMPLETED = "completada"
    REJECTED = "rechazada"


class PriorityEnum(str, Enum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"


class InstitutionalRequestCreate(BaseModel):
    external_id: str = Field(..., min_length=1, max_length=100, description="Unique external identifier")
    requester_name: str = Field(..., min_length=1, max_length=255)
    requester_email: EmailStr
    institution_name: str = Field(..., min_length=1, max_length=255)
    request_type: RequestTypeEnum
    description: str = Field(..., min_length=10, max_length=5000)
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)


class InstitutionalRequestUpdate(BaseModel):
    requester_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[PriorityEnum] = None


class InstitutionalRequestStatusUpdate(BaseModel):
    status: RequestStatusEnum = Field(..., description="New status for the request")


class InstitutionalRequestResponse(BaseModel):
    id: int
    request_number: str
    external_id: str
    requester_name: str
    requester_email: str
    institution_name: str
    request_type: RequestTypeEnum
    description: str
    priority: PriorityEnum
    status: RequestStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    environment: str


class ReadinessCheckResponse(BaseModel):
    status: str
    database: str
    version: str
