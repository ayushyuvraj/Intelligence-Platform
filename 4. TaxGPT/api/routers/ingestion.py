"""FAISS index ingestion endpoints"""
import threading
import uuid
from fastapi import APIRouter
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api.schemas.ingestion import IngestionStartRequest, IngestionStartResponse
from api.schemas.common import IngestionStatusResponse
from api.state import ingestion_state
from ingest import PDFIngestionPipeline

router = APIRouter(prefix="/api/v1", tags=["ingestion"])


def run_ingestion():
    """Background task to run PDF ingestion"""
    try:
        ingestion_state.status = "running"
        ingestion_state.progress_pct = 0

        # Create pipeline and run
        pipeline = PDFIngestionPipeline()
        pipeline.run()

        ingestion_state.status = "complete"
        ingestion_state.progress_pct = 100
        ingestion_state.messages.append("[OK] FAISS index built successfully")
    except Exception as e:
        ingestion_state.status = "failed"
        ingestion_state.error_message = str(e)
        ingestion_state.messages.append(f"[ERROR] Ingestion failed: {str(e)}")


@router.post("/ingestion/start", response_model=IngestionStartResponse)
async def start_ingestion(request: IngestionStartRequest) -> IngestionStartResponse:
    """Start FAISS index ingestion in background"""
    # Check if already running
    if ingestion_state.status == "running":
        return IngestionStartResponse(
            job_id=ingestion_state.job_id,
            status="already_running"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())
    ingestion_state.job_id = job_id

    # Start background thread
    thread = threading.Thread(target=run_ingestion, daemon=False)
    ingestion_state.thread = thread
    thread.start()

    return IngestionStartResponse(job_id=job_id, status="started")


@router.get("/ingestion/status", response_model=IngestionStatusResponse)
async def get_ingestion_status() -> IngestionStatusResponse:
    """Get current ingestion status and progress"""
    # Get last 20 log messages
    log_tail = list(ingestion_state.messages)[-20:]

    return IngestionStatusResponse(
        status=ingestion_state.status,
        progress_pct=ingestion_state.progress_pct,
        message=ingestion_state.error_message or f"Ingestion {ingestion_state.status}",
        log_tail=log_tail,
    )
