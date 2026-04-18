"""Health check endpoint"""
import os
from fastapi import APIRouter
from api.schemas.common import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health and FAISS index status"""
    index_ready = os.path.exists("data/faiss_index/index.faiss")
    provider = os.environ.get("LLM_PROVIDER", "gemini")

    return HealthResponse(
        status="healthy",
        index_ready=index_ready,
        provider=provider
    )
