import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import InstitutionalRequest, RequestStatusEnum
from app.schemas import (
    InstitutionalRequestCreate,
    InstitutionalRequestUpdate,
    InstitutionalRequestStatusUpdate,
)


class InstitutionalRequestService:
    @staticmethod
    def create_request(db: Session, request_data: InstitutionalRequestCreate) -> InstitutionalRequest:
        """Create a new institutional request with unique request number and external ID."""
        request_number = f"SOL-{uuid.uuid4().hex[:8].upper()}"
        db_request = InstitutionalRequest(
            request_number=request_number,
            external_id=request_data.external_id,
            requester_name=request_data.requester_name,
            requester_email=request_data.requester_email,
            institution_name=request_data.institution_name,
            request_type=request_data.request_type,
            description=request_data.description,
            priority=request_data.priority,
        )
        try:
            db.add(db_request)
            db.commit()
            db.refresh(db_request)
            return db_request
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Duplicate external_id: {request_data.external_id}") from e

    @staticmethod
    def get_request(db: Session, request_id: int) -> InstitutionalRequest | None:
        return db.query(InstitutionalRequest).filter(InstitutionalRequest.id == request_id).first()

    @staticmethod
    def get_request_by_external_id(db: Session, external_id: str) -> InstitutionalRequest | None:
        return db.query(InstitutionalRequest).filter(
            InstitutionalRequest.external_id == external_id
        ).first()

    @staticmethod
    def list_requests(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        request_type: str | None = None,
        priority: str | None = None,
    ) -> list[InstitutionalRequest]:
        query = db.query(InstitutionalRequest)

        if status:
            query = query.filter(InstitutionalRequest.status == status)
        if request_type:
            query = query.filter(InstitutionalRequest.request_type == request_type)
        if priority:
            query = query.filter(InstitutionalRequest.priority == priority)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_request(
        db: Session, request_id: int, update_data: InstitutionalRequestUpdate
    ) -> InstitutionalRequest | None:
        db_request = InstitutionalRequestService.get_request(db, request_id)
        if not db_request:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_request, key, value)

        db.commit()
        db.refresh(db_request)
        return db_request

    @staticmethod
    def update_request_status(
        db: Session, request_id: int, status_update: InstitutionalRequestStatusUpdate
    ) -> InstitutionalRequest | None:
        db_request = InstitutionalRequestService.get_request(db, request_id)
        if not db_request:
            return None

        db_request.status = status_update.status
        db.commit()
        db.refresh(db_request)
        return db_request

    @staticmethod
    def delete_request(db: Session, request_id: int) -> bool:
        db_request = InstitutionalRequestService.get_request(db, request_id)
        if not db_request:
            return False

        db.delete(db_request)
        db.commit()
        return True
