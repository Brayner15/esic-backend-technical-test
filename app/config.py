import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ESIC Backend Technical Test"
    app_env: str = os.getenv("APP_ENV", "development")
    app_debug: bool = os.getenv("APP_DEBUG", "True").lower() == "true"
    app_log_level: str = os.getenv("APP_LOG_LEVEL", "INFO")

    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", 8000))
    server_reload: bool = os.getenv("SERVER_RELOAD", "True").lower() == "true"

    # Database URL is REQUIRED - no default allowed
    database_url: str = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    database_pool_recycle: int = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))

    external_service_url: str = os.getenv("EXTERNAL_SERVICE_URL", "http://external-service:8001")
    external_service_timeout: int = int(os.getenv("EXTERNAL_SERVICE_TIMEOUT", "30"))

    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")

    class Config:
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
