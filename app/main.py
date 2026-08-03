import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine, Base, get_db
from app.api import routes
from app.schemas import HealthCheckResponse, ReadinessCheckResponse

settings = get_settings()

logging.basicConfig(level=settings.app_log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Backend service for institutional requests management",
    lifespan=lifespan,
)

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
        logger.error(f"Database connection check failed: {str(e)}")
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
