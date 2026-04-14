"""
RegRadar FastAPI Application

Main entry point for the RegRadar API server.
Handles initialization, middleware, health checks, and error handling.
"""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from src.config import settings
from src.database import init_db, close_db, DatabaseManager, get_db
from src.utils.logger import setup_logging, get_logger, correlation_id_var, generate_correlation_id
from src.utils.errors import RegRadarException

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown."""
    # STARTUP
    logger.info("=" * 60)
    logger.info("RegRadar API Starting Up")
    logger.info("=" * 60)

    try:
        # Initialize logging
        setup_logging()
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")

        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")

        logger.info("RegRadar API Ready")
        logger.info("=" * 60)

    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}")
        raise

    yield

    # SHUTDOWN
    logger.info("=" * 60)
    logger.info("RegRadar API Shutting Down")
    logger.info("=" * 60)

    try:
        await close_db()
        logger.info("Database connection closed")

    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

    logger.info("RegRadar API Stopped")
    logger.info("=" * 60)


# Create FastAPI app
app = FastAPI(
    title="RegRadar API",
    description="AI-powered regulatory intelligence platform for India",
    version="1.0.0",
    lifespan=lifespan,
)


# Middleware: Correlation ID
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to each request for tracing."""
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = generate_correlation_id()

    correlation_id_var.set(correlation_id)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# Middleware: Request logging
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": int(process_time * 1000),
        },
    )

    return response


# Middleware: Error handling
@app.middleware("http")
async def error_handler_middleware(request: Request, call_next):
    """Handle exceptions and convert to proper HTTP responses."""
    try:
        response = await call_next(request)
        return response
    except RegRadarException as e:
        logger.error(
            f"Application error: {e.message}",
            extra={
                "error_code": e.error_code,
                "status_code": e.status_code,
                "details": e.details,
            },
        )
        return JSONResponse(
            status_code=e.status_code,
            content=e.to_dict(),
        )
    except Exception as e:
        logger.error(
            f"Unexpected error: {str(e)}",
            extra={
                "error_type": type(e).__name__,
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "status_code": 500,
            },
        )


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host middleware - allow both production and test hosts
allowed_hosts = [
    settings.backend_url.replace("http://", "").replace("https://", ""),
    "localhost",
    "127.0.0.1",
    "localhost:8000",
]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Dictionary with health status and metadata
    """
    start_time = time.time()

    # Check database connection
    db_connected = DatabaseManager.check_connection()
    table_count = DatabaseManager.get_table_count()

    response_time_ms = int((time.time() - start_time) * 1000)

    health_data = {
        "status": "ok" if db_connected else "degraded",
        "version": "1.0.0",
        "database": {
            "connected": db_connected,
            "table_count": table_count,
        },
        "environment": settings.environment,
        "response_time_ms": response_time_ms,
    }

    logger.info(
        "Health check completed",
        extra={
            "db_connected": db_connected,
            "table_count": table_count,
            "response_time_ms": response_time_ms,
        },
    )

    return health_data


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "service": "RegRadar API",
        "version": "1.0.0",
        "description": "AI-powered regulatory intelligence platform for India",
        "docs_url": "/docs",
        "health_url": "/health",
    }


# Include routers (to be added as features are implemented)
# from src.api.routes import router
# app.include_router(router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_config=None,  # Use our custom logging
    )
