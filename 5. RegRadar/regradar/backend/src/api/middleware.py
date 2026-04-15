"""
API Middleware

Provides HTTP middleware for request/response handling, error handling,
compression, and other cross-cutting concerns.
"""

import time
import json
from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.utils.logger import get_logger
from src.utils.errors import RegRadarException
import uuid

logger = get_logger(__name__)


async def correlation_id_middleware(request: Request, call_next):
    """
    Middleware to add correlation ID to all requests.

    Generates a unique ID for request tracing across logs.
    """
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:16])
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


async def error_handler_middleware(request: Request, call_next):
    """
    Middleware for global error handling.

    Catches exceptions and converts them to proper HTTP responses.
    """
    try:
        response = await call_next(request)
        return response
    except RegRadarException as e:
        # Custom RegRadar exception
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        logger.error(
            e.message,
            extra={
                "error_code": e.error_code,
                "status_code": e.status_code,
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": e.message,
                "error_code": e.error_code,
                "status_code": e.status_code,
                "correlation_id": correlation_id,
                "details": e.details,
            },
        )
    except Exception as e:
        # Unexpected error
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        logger.error(
            f"Unhandled error in {request.method} {request.url.path}: {str(e)}",
            extra={
                "error_type": type(e).__name__,
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "traceback": str(e),
            },
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "status_code": 500,
                "correlation_id": correlation_id,
            },
        )


async def request_timing_middleware(request: Request, call_next):
    """
    Middleware to measure request processing time.

    Adds X-Process-Time header to responses.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms

    response.headers["X-Process-Time-Ms"] = str(int(process_time))

    # Log slow requests
    if process_time > 1000:  # More than 1 second
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        logger.warning(
            f"Slow request: {request.method} {request.url.path}",
            extra={
                "correlation_id": correlation_id,
                "response_time_ms": int(process_time),
                "method": request.method,
                "path": request.url.path,
            },
        )

    return response


async def request_body_logging_middleware(request: Request, call_next):
    """
    Middleware to log request details.

    Logs method, path, query params for debugging.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    # Log request
    logger.debug(
        f"{request.method} {request.url.path}",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
        },
    )

    response = await call_next(request)
    return response


async def security_headers_middleware(request: Request, call_next):
    """
    Middleware to add security headers to responses.

    Adds headers for XSS, CSRF, and other protections.
    """
    response = await call_next(request)

    # HTTPS enforcement
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # XSS prevention
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # CSRF prevention
    response.headers["X-CSRF-Token"] = getattr(request.state, "correlation_id", "")

    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response
