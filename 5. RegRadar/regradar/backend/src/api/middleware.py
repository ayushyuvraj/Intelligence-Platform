"""
API Middleware

Provides HTTP middleware for request/response handling, error handling,
compression, and other cross-cutting concerns.
"""

import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.utils.logger import get_logger, log_event

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Middleware for global error handling.

    Catches exceptions and converts them to proper HTTP responses.
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(
            f"Unhandled error in {request.method} {request.url.path}: {str(e)}",
            extra={
                "error_type": type(e).__name__,
                "method": request.method,
                "path": request.url.path,
            },
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "status_code": 500,
            },
        )


async def request_timing_middleware(request: Request, call_next):
    """
    Middleware to measure request processing time.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)
    return response
