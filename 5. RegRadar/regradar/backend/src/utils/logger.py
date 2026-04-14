"""
Structured JSON Logging Configuration

Provides production-grade structured logging with correlation IDs,
context management, and JSON formatting for log aggregation.
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Any
from pythonjsonlogger import jsonlogger
from src.config import settings


class CorrelationIDVar:
    """Context variable for request correlation ID."""

    _instance: Optional["CorrelationIDVar"] = None
    _id: Optional[str] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set(self, correlation_id: str) -> None:
        """Set correlation ID for current request."""
        self._id = correlation_id

    def get(self) -> str:
        """Get correlation ID, generate if not set."""
        if self._id is None:
            self._id = str(uuid.uuid4())
        return self._id

    def clear(self) -> None:
        """Clear correlation ID."""
        self._id = None


correlation_id_var = CorrelationIDVar()


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with enhanced context information."""

    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['correlation_id'] = correlation_id_var.get()

        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
            log_record['exc_type'] = record.exc_info[0].__name__ if record.exc_info[0] else None

        # Remove default fields we don't want
        log_record.pop('asctime', None)
        log_record.pop('msecs', None)
        log_record.pop('relativeCreated', None)


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure structured JSON logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   Defaults to settings.log_level if not provided
    """
    if log_level is None:
        log_level = settings.log_level

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler with JSON format
    console_handler = logging.StreamHandler()
    formatter = CustomJsonFormatter()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set level for third-party loggers to reduce noise
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding structured context to logs."""

    def __init__(self, **context: Any):
        """
        Initialize log context.

        Args:
            **context: Key-value pairs to add to all logs within this context
        """
        self.context = context
        self._old_extra = None

    def __enter__(self):
        """Enter context."""
        # Store context in thread-local storage for handlers to access
        # (This is a simplified version; in production use contextvars)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        return False

    def log(self, logger: logging.Logger, level: str, message: str) -> None:
        """Log message with context."""
        log_func = getattr(logger, level.lower())
        log_func(message, extra=self.context)


def log_event(
    logger: logging.Logger,
    level: str,
    message: str,
    **context: Any
) -> None:
    """
    Log an event with structured context.

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **context: Additional context fields
    """
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=context)
