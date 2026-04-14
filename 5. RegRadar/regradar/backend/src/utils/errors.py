"""
Custom Exception Classes

Production-grade exceptions with proper error codes and safe messages.
"""

from fastapi import HTTPException, status
from typing import Optional, Any


class RegRadarException(Exception):
    """Base exception for RegRadar application."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "error": self.message,
            "error_code": self.error_code,
            "status_code": self.status_code,
            "details": self.details,
        }


class ValidationException(RegRadarException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        """
        Initialize validation exception.

        Args:
            message: Error message
            field: Field name that failed validation
            value: The invalid value
        """
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class DatabaseException(RegRadarException):
    """Raised when database operations fail."""

    def __init__(self, message: str, operation: Optional[str] = None):
        """
        Initialize database exception.

        Args:
            message: Error message
            operation: Database operation that failed
        """
        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class NotFoundException(RegRadarException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: Any):
        """
        Initialize not found exception.

        Args:
            resource_type: Type of resource (e.g., 'regulation')
            resource_id: ID of the missing resource
        """
        super().__init__(
            message=f"{resource_type} not found",
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": str(resource_id)},
        )


class AIProcessingException(RegRadarException):
    """Raised when AI processing fails."""

    def __init__(
        self,
        message: str,
        attempt_number: int = 1,
        should_retry: bool = False,
    ):
        """
        Initialize AI processing exception.

        Args:
            message: Error message
            attempt_number: Which attempt number failed
            should_retry: Whether the operation should be retried
        """
        super().__init__(
            message=message,
            error_code="AI_PROCESSING_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={
                "attempt_number": attempt_number,
                "should_retry": should_retry,
            },
        )


class ScraperException(RegRadarException):
    """Raised when scraper operations fail."""

    def __init__(
        self,
        message: str,
        source_body: str,
        error_type: Optional[str] = None,
    ):
        """
        Initialize scraper exception.

        Args:
            message: Error message
            source_body: Which scraper failed (RBI, SEBI, etc)
            error_type: Type of error (network, parsing, timeout, etc)
        """
        super().__init__(
            message=message,
            error_code="SCRAPER_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"source_body": source_body, "error_type": error_type},
        )


class RateLimitException(RegRadarException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after_seconds: int = 60):
        """
        Initialize rate limit exception.

        Args:
            message: Error message
            retry_after_seconds: How long to wait before retrying
        """
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after_seconds": retry_after_seconds},
        )


class UnauthorizedException(RegRadarException):
    """Raised when authentication/authorization fails."""

    def __init__(self, message: str = "Unauthorized"):
        """Initialize unauthorized exception."""
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(RegRadarException):
    """Raised when access is forbidden."""

    def __init__(self, message: str = "Forbidden"):
        """Initialize forbidden exception."""
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )
