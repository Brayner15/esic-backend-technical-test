from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="External Service", version="0.1.0")


class ExternalRequest(BaseModel):
    request_number: str
    requester_name: str
    institution_name: str


class ExternalResponse(BaseModel):
    external_reference_id: str
    status: str
    message: str


@app.post("/process-request", response_model=ExternalResponse)
def process_request(request: ExternalRequest):
    """
    Simulates an external service processing a request.
    This would be a real integration point in production.
    """
    external_id = f"EXT-{uuid.uuid4().hex[:12].upper()}"
    logger.info(f"Processing request {request.request_number} with external ID {external_id}")

    return ExternalResponse(
        external_reference_id=external_id,
        status="accepted",
        message=f"Request {request.request_number} has been accepted by external system",
    )


@app.get("/health")
def health():
    return {"status": "healthy", "service": "external-service"}
