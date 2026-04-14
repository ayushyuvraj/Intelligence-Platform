"""
API Dependencies

Provides reusable dependencies for FastAPI route handlers.
Used for session validation, database access, permission checks, etc.
"""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def verify_session_id(
    x_session_id: str = Header(...),
    db: Session = Depends(get_db),
) -> dict:
    """
    Verify session ID from request header.

    Args:
        x_session_id: Session ID from X-Session-ID header
        db: Database session

    Returns:
        Session data

    Raises:
        HTTPException: If session not found or invalid
    """
    # TODO: Implement session validation
    if not x_session_id or len(x_session_id) < 32:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID",
        )

    return {"session_id": x_session_id}


async def verify_api_key(
    x_api_key: str = Header(None),
) -> str:
    """
    Verify API key for scraper requests.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key invalid
    """
    # TODO: Implement API key verification for scraper access
    if x_api_key:
        return x_api_key

    # Scraper API key is optional for now, required in Phase 2
    return None
