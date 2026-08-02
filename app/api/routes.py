from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    InstitutionalRequestCreate,
    InstitutionalRequestResponse,
    InstitutionalRequestUpdate,
)
from app.services import InstitutionalRequestService

router = APIRouter(prefix="/api/v1/requests", tags=["requests"])


@router.post("/", response_model=InstitutionalRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(request: InstitutionalRequestCreate, db: Session = Depends(get_db)):
    created_request = InstitutionalRequestService.create_request(db, request)
    return created_request


@router.get("/{request_id}", response_model=InstitutionalRequestResponse)
def get_request(request_id: int, db: Session = Depends(get_db)):
    db_request = InstitutionalRequestService.get_request(db, request_id)
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return db_request


@router.get("/", response_model=list[InstitutionalRequestResponse])
def list_requests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return InstitutionalRequestService.list_requests(db, skip=skip, limit=limit)


@router.put("/{request_id}", response_model=InstitutionalRequestResponse)
def update_request(
    request_id: int, request: InstitutionalRequestUpdate, db: Session = Depends(get_db)
):
    db_request = InstitutionalRequestService.update_request(db, request_id, request)
    if not db_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return db_request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    success = InstitutionalRequestService.delete_request(db, request_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
