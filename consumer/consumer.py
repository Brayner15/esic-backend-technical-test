import httpx
import logging
from typing import Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
                )

                if response.status_code == 201:
                    result = response.json()
                    logger.info(
                        f"✓ Successfully created request {external_id} | "
                        f"ID: {result['id']} | Attempt: {attempt}"
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
                        f"✗ Duplicate request {external_id} (409 Conflict) | "
                        f"Not retrying"
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
                        f"✗ Client error creating request {external_id} | "
                        f"Status: {response.status_code} | Not retrying"
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
                        f"⟳ Retryable error creating request {external_id} | "
                        f"Status: {response.status_code} | Attempt: {attempt}/{self.max_retries}"
                    )
                    if attempt < self.max_retries:
                        import time
                        time.sleep(self.retry_delay)
                    attempt += 1
                else:
                    logger.error(
                        f"✗ Unexpected error creating request {external_id} | "
                        f"Status: {response.status_code}"
                    )
                    return None

            except httpx.TimeoutException as e:
                logger.warning(
                    f"⟳ Timeout creating request {external_id} | "
                    f"Attempt: {attempt}/{self.max_retries}"
                )
                if attempt < self.max_retries:
                    import time
                    time.sleep(self.retry_delay)
                attempt += 1

            except httpx.ConnectError as e:
                logger.warning(
                    f"⟳ Connection error creating request {external_id} | "
                    f"Attempt: {attempt}/{self.max_retries}"
                )
                if attempt < self.max_retries:
                    import time
                    time.sleep(self.retry_delay)
                attempt += 1

            except Exception as e:
                logger.error(
                    f"✗ Unexpected error creating request {external_id}: {str(e)}"
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
            f"✗ Failed to create request {external_id} after {self.max_retries} attempts"
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
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    f"✓ Retrieved request {external_id} | "
                    f"Status: {result['status']}"
                )
                return result
            else:
                logger.error(
                    f"✗ Failed to retrieve request {external_id} | "
                    f"Status: {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(
                f"✗ Error retrieving request {external_id}: {str(e)}"
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
                logger.info("✓ Backend is healthy")
                return True
            else:
                logger.error(f"✗ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Backend connection error: {str(e)}")
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
                    f"✓ Backend is ready | Database: {data['database']}"
                )
                return True
            else:
                logger.error(
                    f"✗ Backend readiness check failed: {response.status_code}"
                )
                return False
        except Exception as e:
            logger.error(f"✗ Backend readiness error: {str(e)}")
            return False

    def print_summary(self):
        """Print execution summary."""
        successful = sum(1 for r in self.results if r["status"] == "success")
        failed = sum(1 for r in self.results if r["status"] in ["failed", "error"])
        conflicts = sum(1 for r in self.results if r["status"] == "conflict")

        logger.info("\n" + "=" * 60)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total attempts: {len(self.results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Conflicts (duplicates): {conflicts}")
        logger.info("=" * 60 + "\n")


def main():
    """Main execution function."""
    consumer = RequestConsumer(
        base_url="http://localhost:8000",
        timeout=30,
        max_retries=3,
        retry_delay=2,
    )

    logger.info("Starting institutional requests consumer service...\n")

    if not consumer.check_health():
        logger.error("Backend is not available. Exiting.")
        return

    if not consumer.check_readiness():
        logger.error("Backend is not ready. Exiting.")
        return

    logger.info("\nCreating institutional requests...\n")

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

    logger.info("\nConsulting request statuses...\n")

    for request in created_requests:
        consumer.get_request(request["id"], request["external_id"])

    consumer.print_summary()


if __name__ == "__main__":
    main()
