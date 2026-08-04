import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.models import InstitutionalRequest, RequestStatusEnum
from app.schemas import (
    InstitutionalRequestCreate,
    InstitutionalRequestUpdate,
    InstitutionalRequestStatusUpdate,
)

logger = logging.getLogger(__name__)


class DuplicateExternalIdError(Exception):
    """Raised when attempting to create a request with a duplicate external_id."""
    pass


class RequestNotFoundError(Exception):
    """Raised when a request is not found."""
    pass


class InstitutionalRequestService:
    """Service for managing institutional requests with transactional support."""

    @staticmethod
    def create_request(db: Session, request_data: InstitutionalRequestCreate) -> InstitutionalRequest:
        """
        Create a new institutional request with unique request number and external ID.

        Raises:
            DuplicateExternalIdError: If external_id already exists
        """
        logger.info(
            "service_create_request_start",
            extra={
                "external_id": request_data.external_id,
                "request_type": request_data.request_type,
            },
        )

        existing_request = db.query(InstitutionalRequest).filter(
            InstitutionalRequest.external_id == request_data.external_id
        ).first()

        if existing_request:
            logger.warning(
                "service_create_request_duplicate_detected",
                extra={
                    "external_id": request_data.external_id,
                    "existing_request_id": existing_request.id,
                },
            )
            raise DuplicateExternalIdError(
                f"Solicitud con external_id '{request_data.external_id}' ya existe (ID: {existing_request.id})"
            )

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

            logger.info(
                "service_create_request_success",
                extra={
                    "external_id": request_data.external_id,
                    "request_id": db_request.id,
                    "request_number": db_request.request_number,
                },
            )
            return db_request

        except IntegrityError as e:
            db.rollback()
            logger.error(
                "service_create_request_integrity_error",
                extra={
                    "external_id": request_data.external_id,
                    "error_detail": str(e.orig),
                },
            )
            if "external_id" in str(e.orig):
                raise DuplicateExternalIdError(
                    f"Solicitud con external_id '{request_data.external_id}' ya existe"
                ) from e
            raise

    @staticmethod
    def get_request(db: Session, request_id: int) -> InstitutionalRequest | None:
        """Get a request by ID."""
        return db.query(InstitutionalRequest).filter(
            InstitutionalRequest.id == request_id
        ).first()

    @staticmethod
    def get_request_by_external_id(db: Session, external_id: str) -> InstitutionalRequest | None:
        """Get a request by external_id."""
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
        """
        List requests with optional filters.

        Filters:
            status: Request status (recibida, en_proceso, completada, rechazada)
            request_type: Request type (acceso_plataforma, soporte_tecnico, academica, administrativa)
            priority: Priority level (baja, media, alta)
        """
        query = db.query(InstitutionalRequest)

        if status:
            query = query.filter(InstitutionalRequest.status == status)
        if request_type:
            query = query.filter(InstitutionalRequest.request_type == request_type)
        if priority:
            query = query.filter(InstitutionalRequest.priority == priority)

        return query.order_by(InstitutionalRequest.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_request(
        db: Session, request_id: int, update_data: InstitutionalRequestUpdate
    ) -> InstitutionalRequest | None:
        """Update request fields (name, description, priority)."""
        db_request = InstitutionalRequestService.get_request(db, request_id)
        if not db_request:
            logger.warning(
                "service_update_request_not_found",
                extra={"request_id": request_id},
            )
            return None

        update_dict = update_data.model_dump(exclude_unset=True)

        logger.info(
            "service_update_request_start",
            extra={
                "request_id": request_id,
                "fields_to_update": list(update_dict.keys()),
            },
        )

        for key, value in update_dict.items():
            setattr(db_request, key, value)

        try:
            db.commit()
            db.refresh(db_request)

            logger.info(
                "service_update_request_success",
                extra={
                    "request_id": request_id,
                    "updated_fields": list(update_dict.keys()),
                },
            )
            return db_request

        except IntegrityError as e:
            db.rollback()
            logger.error(
                "service_update_request_error",
                extra={
                    "request_id": request_id,
                    "error_detail": str(e.orig),
                },
            )
            raise

    @staticmethod
    def update_request_status(
        db: Session, request_id: int, status_update: InstitutionalRequestStatusUpdate
    ) -> InstitutionalRequest | None:
        """Update only the status field with validation."""
        db_request = InstitutionalRequestService.get_request(db, request_id)
        if not db_request:
            logger.warning(
                "service_update_status_not_found",
                extra={"request_id": request_id},
            )
            return None

        old_status = db_request.status

        logger.info(
            "service_update_status_start",
            extra={
                "request_id": request_id,
                "old_status": old_status,
                "new_status": status_update.status,
            },
        )

        db_request.status = status_update.status

        try:
            db.commit()
            db.refresh(db_request)

            logger.info(
                "service_update_status_success",
                extra={
                    "request_id": request_id,
                    "old_status": old_status,
                    "new_status": status_update.status,
                },
            )
            return db_request

        except IntegrityError as e:
            db.rollback()
            logger.error(
                "service_update_status_error",
                extra={
                    "request_id": request_id,
                    "error_detail": str(e.orig),
                },
            )
            raise

    @staticmethod
    def delete_request(db: Session, request_id: int) -> bool:
        """Delete a request by ID."""
        db_request = InstitutionalRequestService.get_request(db, request_id)
        if not db_request:
            logger.warning(
                "service_delete_request_not_found",
                extra={"request_id": request_id},
            )
            return False

        logger.info(
            "service_delete_request_start",
            extra={
                "request_id": request_id,
                "external_id": db_request.external_id,
            },
        )

        try:
            db.delete(db_request)
            db.commit()

            logger.info(
                "service_delete_request_success",
                extra={
                    "request_id": request_id,
                    "external_id": db_request.external_id,
                },
            )
            return True

        except IntegrityError as e:
            db.rollback()
            logger.error(
                "service_delete_request_error",
                extra={
                    "request_id": request_id,
                    "error_detail": str(e.orig),
                },
            )
            raise
