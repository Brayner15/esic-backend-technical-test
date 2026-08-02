import uuid
from sqlalchemy.orm import Session
from app.models import InstitutionalRequest, RequestStatusEnum
from app.schemas import InstitutionalRequestCreate, InstitutionalRequestUpdate


class InstitutionalRequestService:
    @staticmethod
    def create_request(db: Session, request_data: InstitutionalRequestCreate) -> InstitutionalRequest:
        request_number = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        db_request = InstitutionalRequest(
            request_number=request_number,
            requester_name=request_data.requester_name,
            requester_email=request_data.requester_email,
            institution_name=request_data.institution_name,
            request_type=request_data.request_type,
            description=request_data.description,
        )
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request

    @staticmethod
    def get_request(db: Session, request_id: int) -> InstitutionalRequest | None:
        return db.query(InstitutionalRequest).filter(InstitutionalRequest.id == request_id).first()

    @staticmethod
    def get_request_by_number(db: Session, request_number: str) -> InstitutionalRequest | None:
        return db.query(InstitutionalRequest).filter(
            InstitutionalRequest.request_number == request_number
        ).first()

    @staticmethod
    def list_requests(db: Session, skip: int = 0, limit: int = 100) -> list[InstitutionalRequest]:
        return db.query(InstitutionalRequest).offset(skip).limit(limit).all()

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
    def delete_request(db: Session, request_id: int) -> bool:
        db_request = InstitutionalRequestService.get_request(db, request_id)
        if not db_request:
            return False

        db.delete(db_request)
        db.commit()
        return True

    @staticmethod
    def update_request_status(
        db: Session, request_id: int, status: RequestStatusEnum
    ) -> InstitutionalRequest | None:
        db_request = InstitutionalRequestService.get_request(db, request_id)
        if not db_request:
            return None

        db_request.status = status
        db.commit()
        db.refresh(db_request)
        return db_request
