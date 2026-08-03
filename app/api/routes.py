import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    InstitutionalRequestCreate,
    InstitutionalRequestResponse,
    InstitutionalRequestUpdate,
    InstitutionalRequestStatusUpdate,
)
from app.services import InstitutionalRequestService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])


@router.post("/", response_model=InstitutionalRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(request: InstitutionalRequestCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva solicitud institucional.

    El campo external_id debe ser único en el sistema.
    """
    try:
        logger.info(
            "create_request_attempt",
            extra={
                "external_id": request.external_id,
                "request_type": request.request_type,
                "priority": request.priority,
            },
        )
        created_request = InstitutionalRequestService.create_request(db, request)
        logger.info(
            "create_request_success",
            extra={
                "external_id": request.external_id,
                "request_id": created_request.id,
                "request_number": created_request.request_number,
            },
        )
        return created_request
    except ValueError as e:
        logger.warning(
            "create_request_duplicate",
            extra={
                "external_id": request.external_id,
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/", response_model=list[InstitutionalRequestResponse])
def list_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None, description="Filtrar por estado"),
    request_type: str | None = Query(None, description="Filtrar por tipo de solicitud"),
    priority: str | None = Query(None, description="Filtrar por prioridad"),
    db: Session = Depends(get_db)
):
    """
    Consultar solicitudes con filtros opcionales.

    Filtros disponibles:
    - status: recibida, en_proceso, completada, rechazada
    - request_type: acceso_plataforma, soporte_tecnico, academica, administrativa
    - priority: baja, media, alta
    """
    logger.info(
        "list_requests",
        extra={
            "skip": skip,
            "limit": limit,
            "filters": {
                "status": status,
                "request_type": request_type,
                "priority": priority,
            },
        },
    )
    return InstitutionalRequestService.list_requests(
        db,
        skip=skip,
        limit=limit,
        status=status,
        request_type=request_type,
        priority=priority
    )


@router.get("/{request_id}", response_model=InstitutionalRequestResponse)
def get_request(request_id: int, db: Session = Depends(get_db)):
    """Consultar una solicitud específica por su ID."""
    logger.info("get_request_attempt", extra={"request_id": request_id})
    db_request = InstitutionalRequestService.get_request(db, request_id)
    if not db_request:
        logger.warning("get_request_not_found", extra={"request_id": request_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    logger.info(
        "get_request_success",
        extra={
            "request_id": request_id,
            "status": db_request.status,
        },
    )
    return db_request


@router.put("/{request_id}", response_model=InstitutionalRequestResponse)
def update_request(
    request_id: int,
    request: InstitutionalRequestUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una solicitud (nombre, descripción o prioridad)."""
    logger.info("update_request_attempt", extra={"request_id": request_id})
    db_request = InstitutionalRequestService.update_request(db, request_id, request)
    if not db_request:
        logger.warning("update_request_not_found", extra={"request_id": request_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    logger.info(
        "update_request_success",
        extra={
            "request_id": request_id,
            "updated_fields": list(request.model_dump(exclude_unset=True).keys()),
        },
    )
    return db_request


@router.patch("/{request_id}/estado", response_model=InstitutionalRequestResponse)
def update_request_status(
    request_id: int,
    status_update: InstitutionalRequestStatusUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar el estado de una solicitud."""
    logger.info(
        "update_status_attempt",
        extra={
            "request_id": request_id,
            "new_status": status_update.status,
        },
    )
    db_request = InstitutionalRequestService.update_request_status(db, request_id, status_update)
    if not db_request:
        logger.warning("update_status_not_found", extra={"request_id": request_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    logger.info(
        "update_status_success",
        extra={
            "request_id": request_id,
            "new_status": status_update.status,
        },
    )
    return db_request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    """Eliminar una solicitud."""
    logger.info("delete_request_attempt", extra={"request_id": request_id})
    success = InstitutionalRequestService.delete_request(db, request_id)
    if not success:
        logger.warning("delete_request_not_found", extra={"request_id": request_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    logger.info("delete_request_success", extra={"request_id": request_id})
