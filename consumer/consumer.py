import httpx
import logging
import json
import uuid
import os
from typing import Optional
from datetime import datetime
from pythonjsonlogger import jsonlogger

os.makedirs("logs", exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler("logs/consumer.log")
file_handler.setLevel(logging.INFO)
file_formatter = jsonlogger.JsonFormatter(
    "%(timestamp)s %(level)s %(logger)s %(message)s %(correlation_id)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(file_formatter)
logger.addHandler(console_handler)


class RequestConsumer:
    """Consumer service that sends requests to the backend API with retry logic."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = httpx.Client(timeout=timeout)
        self.results = []
        self.correlation_id = str(uuid.uuid4())

    def is_retryable_error(self, status_code: int) -> bool:
        """Determine if an error is retryable."""
        if status_code >= 500:
            return True
        return status_code in [408, 429]

    def create_request(
        self,
        external_id: str,
        requester_name: str,
        requester_email: str,
        institution_name: str,
        request_type: str,
        description: str,
        priority: str = "media",
    ) -> Optional[dict]:
        """
        Create an institutional request with automatic retry logic.

        Returns the created request or None if it fails permanently.
        """
        payload = {
            "external_id": external_id,
            "requester_name": requester_name,
            "requester_email": requester_email,
            "institution_name": institution_name,
            "request_type": request_type,
            "description": description,
            "priority": priority,
        }

        attempt = 1
        while attempt <= self.max_retries:
            try:
                response = self.client.post(
                    f"{self.base_url}/solicitudes/",
                    json=payload,
                    timeout=self.timeout,
                    headers={"X-Correlation-ID": self.correlation_id},
                )

                if response.status_code == 201:
                    result = response.json()
                    logger.info(
                        "create_request_success",
                        extra={
                            "correlation_id": self.correlation_id,
                            "external_id": external_id,
                            "request_id": result["id"],
                            "request_number": result["request_number"],
                            "attempt": attempt,
                            "status_code": 201,
                        },
                    )
                    self.results.append({
                        "external_id": external_id,
                        "status": "success",
                        "request_id": result["id"],
                        "attempt": attempt,
                        "timestamp": datetime.now().isoformat(),
                    })
                    return result

                elif response.status_code == 409:
                    logger.warning(
                        "create_request_conflict",
                        extra={
                            "correlation_id": self.correlation_id,
                            "external_id": external_id,
                            "status_code": 409,
                            "error_detail": "Duplicate external_id",
                        },
                    )
                    self.results.append({
                        "external_id": external_id,
                        "status": "conflict",
                        "error": "Duplicate external_id",
                        "attempt": attempt,
                        "timestamp": datetime.now().isoformat(),
                    })
                    return None

                elif response.status_code >= 400 and response.status_code < 500:
                    logger.error(
                        "create_request_client_error",
                        extra={
                            "correlation_id": self.correlation_id,
                            "external_id": external_id,
                            "status_code": response.status_code,
                            "attempt": attempt,
                            "retry": False,
                        },
                    )
                    self.results.append({
                        "external_id": external_id,
                        "status": "error",
                        "error": f"HTTP {response.status_code}",
                        "attempt": attempt,
                        "timestamp": datetime.now().isoformat(),
                    })
                    return None

                elif self.is_retryable_error(response.status_code):
                    logger.warning(
                        "create_request_retryable_error",
                        extra={
                            "correlation_id": self.correlation_id,
                            "external_id": external_id,
                            "status_code": response.status_code,
                            "retry_attempt": attempt,
                            "max_retries": self.max_retries,
                        },
                    )
                    if attempt < self.max_retries:
                        import time
                        time.sleep(self.retry_delay)
                    attempt += 1
                else:
                    logger.error(
                        "create_request_unexpected_error",
                        extra={
                            "correlation_id": self.correlation_id,
                            "external_id": external_id,
                            "status_code": response.status_code,
                        },
                    )
                    return None

            except httpx.TimeoutException:
                logger.warning(
                    "create_request_timeout",
                    extra={
                        "correlation_id": self.correlation_id,
                        "external_id": external_id,
                        "retry_attempt": attempt,
                        "max_retries": self.max_retries,
                    },
                )
                if attempt < self.max_retries:
                    import time
                    time.sleep(self.retry_delay)
                attempt += 1

            except httpx.ConnectError:
                logger.warning(
                    "create_request_connection_error",
                    extra={
                        "correlation_id": self.correlation_id,
                        "external_id": external_id,
                        "retry_attempt": attempt,
                        "max_retries": self.max_retries,
                    },
                )
                if attempt < self.max_retries:
                    import time
                    time.sleep(self.retry_delay)
                attempt += 1

            except Exception as e:
                logger.error(
                    "create_request_unexpected_exception",
                    extra={
                        "correlation_id": self.correlation_id,
                        "external_id": external_id,
                        "error_detail": str(e),
                    },
                )
                self.results.append({
                    "external_id": external_id,
                    "status": "error",
                    "error": str(e),
                    "attempt": attempt,
                    "timestamp": datetime.now().isoformat(),
                })
                return None

        logger.error(
            "create_request_max_retries_exceeded",
            extra={
                "correlation_id": self.correlation_id,
                "external_id": external_id,
                "max_retries": self.max_retries,
            },
        )
        self.results.append({
            "external_id": external_id,
            "status": "failed",
            "error": "Max retries exceeded",
            "attempts": self.max_retries,
            "timestamp": datetime.now().isoformat(),
        })
        return None

    def get_request(self, request_id: int, external_id: str) -> Optional[dict]:
        """Get request status."""
        try:
            response = self.client.get(
                f"{self.base_url}/solicitudes/{request_id}",
                timeout=self.timeout,
                headers={"X-Correlation-ID": self.correlation_id},
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    "get_request_success",
                    extra={
                        "correlation_id": self.correlation_id,
                        "external_id": external_id,
                        "request_id": request_id,
                        "status": result["status"],
                        "status_code": 200,
                    },
                )
                return result
            else:
                logger.error(
                    "get_request_error",
                    extra={
                        "correlation_id": self.correlation_id,
                        "external_id": external_id,
                        "request_id": request_id,
                        "status_code": response.status_code,
                    },
                )
                return None

        except Exception as e:
            logger.error(
                "get_request_exception",
                extra={
                    "correlation_id": self.correlation_id,
                    "external_id": external_id,
                    "request_id": request_id,
                    "error_detail": str(e),
                },
            )
            return None

    def check_health(self) -> bool:
        """Check if the backend is healthy."""
        try:
            response = self.client.get(
                f"{self.base_url}/health",
                timeout=5,
            )
            if response.status_code == 200:
                logger.info(
                    "health_check_success",
                    extra={
                        "correlation_id": self.correlation_id,
                        "service": "backend",
                        "status_code": 200,
                    },
                )
                return True
            else:
                logger.error(
                    "health_check_failed",
                    extra={
                        "correlation_id": self.correlation_id,
                        "service": "backend",
                        "status_code": response.status_code,
                    },
                )
                return False
        except Exception as e:
            logger.error(
                "health_check_exception",
                extra={
                    "correlation_id": self.correlation_id,
                    "service": "backend",
                    "error_detail": str(e),
                },
            )
            return False

    def check_readiness(self) -> bool:
        """Check if the backend is ready (including database connection)."""
        try:
            response = self.client.get(
                f"{self.base_url}/health/ready",
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                logger.info(
                    "readiness_check_success",
                    extra={
                        "correlation_id": self.correlation_id,
                        "service": "backend",
                        "database": data["database"],
                        "status_code": 200,
                    },
                )
                return True
            else:
                logger.error(
                    "readiness_check_failed",
                    extra={
                        "correlation_id": self.correlation_id,
                        "service": "backend",
                        "status_code": response.status_code,
                    },
                )
                return False
        except Exception as e:
            logger.error(
                "readiness_check_exception",
                extra={
                    "correlation_id": self.correlation_id,
                    "service": "backend",
                    "error_detail": str(e),
                },
            )
            return False

    def print_summary(self):
        """Print execution summary."""
        successful = sum(1 for r in self.results if r["status"] == "success")
        failed = sum(1 for r in self.results if r["status"] in ["failed", "error"])
        conflicts = sum(1 for r in self.results if r["status"] == "conflict")

        logger.info(
            "execution_summary",
            extra={
                "correlation_id": self.correlation_id,
                "total_attempts": len(self.results),
                "successful": successful,
                "failed": failed,
                "conflicts": conflicts,
            },
        )


def main():
    """Main execution function."""
    consumer = RequestConsumer(
        base_url="http://backend:8000",
        timeout=30,
        max_retries=3,
        retry_delay=2,
    )

    logger.info(
        "consumer_started",
        extra={
            "correlation_id": consumer.correlation_id,
            "backend_url": consumer.base_url,
        },
    )

    if not consumer.check_health():
        logger.error(
            "consumer_backend_unavailable",
            extra={"correlation_id": consumer.correlation_id},
        )
        return

    if not consumer.check_readiness():
        logger.error(
            "consumer_backend_not_ready",
            extra={"correlation_id": consumer.correlation_id},
        )
        return

    logger.info(
        "creating_requests",
        extra={"correlation_id": consumer.correlation_id},
    )

    requests_to_create = [
        {
            "external_id": "EXT-001",
            "requester_name": "Juan Pérez",
            "requester_email": "juan@example.com",
            "institution_name": "Universidad Nacional",
            "request_type": "academica",
            "description": "Solicitud de información sobre programas académicos disponibles en la institución",
            "priority": "alta",
        },
        {
            "external_id": "EXT-002",
            "requester_name": "María García",
            "requester_email": "maria@example.com",
            "institution_name": "Instituto Técnico",
            "request_type": "soporte_tecnico",
            "description": "Problema de acceso a la plataforma de aprendizaje virtual de la institución",
            "priority": "alta",
        },
        {
            "external_id": "EXT-003",
            "requester_name": "Carlos López",
            "requester_email": "carlos@example.com",
            "institution_name": "Colegio Técnico",
            "request_type": "administrativa",
            "description": "Solicitud de cambio de horario de clases para el próximo semestre académico",
            "priority": "media",
        },
        {
            "external_id": "EXT-004",
            "requester_name": "Ana Martínez",
            "requester_email": "ana@example.com",
            "institution_name": "Universidad Central",
            "request_type": "acceso_plataforma",
            "description": "Necesito acceso a la plataforma de gestión de becas y financiamiento estudiantil",
            "priority": "baja",
        },
        {
            "external_id": "EXT-005",
            "requester_name": "Roberto Silva",
            "requester_email": "roberto@example.com",
            "institution_name": "Instituto Profesional",
            "request_type": "academica",
            "description": "Consulta sobre disponibilidad de cursos de especialización en el área de tecnología",
            "priority": "media",
        },
    ]

    created_requests = []
    for req_data in requests_to_create:
        result = consumer.create_request(**req_data)
        if result:
            created_requests.append(result)

    logger.info(
        "consulting_status",
        extra={
            "correlation_id": consumer.correlation_id,
            "requests_created": len(created_requests),
        },
    )

    for request in created_requests:
        consumer.get_request(request["id"], request["external_id"])

    consumer.print_summary()


if __name__ == "__main__":
    main()
