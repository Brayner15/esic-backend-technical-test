import logging
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine, Base, get_db
from app.api import routes
from app.schemas import HealthCheckResponse, ReadinessCheckResponse
from app.logging_config import setup_logging
from app.middleware import LoggingMiddleware

settings = get_settings()

os.makedirs("logs", exist_ok=True)
logger = setup_logging(
    __name__,
    log_file="logs/application.log"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup", extra={"environment": settings.app_env})
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("application_shutdown")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend service for institutional requests management",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)


@app.get("/health", response_model=HealthCheckResponse)
def health_check():
    """Verificar disponibilidad de la API."""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.app_env,
    )


@app.get("/health/ready", response_model=ReadinessCheckResponse)
def readiness_check(db: Session = Depends(get_db)):
    """Verificar que la API esté lista: disponibilidad y conexión con PostgreSQL."""
    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception as e:
        logger.error(
            "database_connection_failed",
            extra={"error_detail": str(e)}
        )
        database_status = "disconnected"

    return ReadinessCheckResponse(
        status="ready" if database_status == "connected" else "not_ready",
        database=database_status,
        version="0.1.0",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_reload,
    )
