import logging
import json
import uuid
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = getattr(
                CorrelationIdFilter, "correlation_id", str(uuid.uuid4())
            )
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that adds additional fields."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["correlation_id"] = getattr(record, "correlation_id", "")

        if hasattr(record, "request_method"):
            log_record["request_method"] = record.request_method
        if hasattr(record, "request_path"):
            log_record["request_path"] = record.request_path
        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
        if hasattr(record, "retry_attempt"):
            log_record["retry_attempt"] = record.retry_attempt
        if hasattr(record, "error_detail"):
            log_record["error_detail"] = record.error_detail


def setup_logging(name: str, log_file: str = None) -> logging.Logger:
    """Configure logging with JSON format."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger.addFilter(CorrelationIdFilter())

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(logger)s %(message)s %(correlation_id)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(logger)s %(message)s %(correlation_id)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context."""
    CorrelationIdFilter.correlation_id = correlation_id
