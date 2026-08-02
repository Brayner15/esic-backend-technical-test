from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class RequestStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstitutionalRequestCreate(BaseModel):
    requester_name: str = Field(..., min_length=1, max_length=255)
    requester_email: EmailStr
    institution_name: str = Field(..., min_length=1, max_length=255)
    request_type: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=5000)


class InstitutionalRequestUpdate(BaseModel):
    requester_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[RequestStatusEnum] = None


class InstitutionalRequestResponse(BaseModel):
    id: int
    request_number: str
    requester_name: str
    requester_email: str
    institution_name: str
    request_type: str
    description: str
    status: RequestStatusEnum
    external_reference_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class HealthCheckResponse(BaseModel):
    status: str
    version: str
    environment: str
