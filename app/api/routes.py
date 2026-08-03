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

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])


@router.post("/", response_model=InstitutionalRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(request: InstitutionalRequestCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva solicitud institucional.

    El campo external_id debe ser único en el sistema.
    """
    try:
        created_request = InstitutionalRequestService.create_request(db, request)
        return created_request
    except ValueError as e:
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
    db_request = InstitutionalRequestService.get_request(db, request_id)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    return db_request


@router.put("/{request_id}", response_model=InstitutionalRequestResponse)
def update_request(
    request_id: int,
    request: InstitutionalRequestUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una solicitud (nombre, descripción o prioridad)."""
    db_request = InstitutionalRequestService.update_request(db, request_id, request)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    return db_request


@router.patch("/{request_id}/estado", response_model=InstitutionalRequestResponse)
def update_request_status(
    request_id: int,
    status_update: InstitutionalRequestStatusUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar el estado de una solicitud."""
    db_request = InstitutionalRequestService.update_request_status(db, request_id, status_update)
    if not db_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
    return db_request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    """Eliminar una solicitud."""
    success = InstitutionalRequestService.delete_request(db, request_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud no encontrada"
        )
