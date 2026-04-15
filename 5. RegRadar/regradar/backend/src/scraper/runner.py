"""
Scraper Runner and Scheduler

Manages scraper execution and scheduling.
Uses APScheduler for background job scheduling.
"""

import asyncio
import time
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from src.database import DatabaseManager, get_db
from src.scraper.sebi import SEBIScraper
from src.scraper.deduplicator import Deduplicator
from src.models import Regulation, ScraperRun
from src.utils.logger import get_logger
from src.utils.errors import ScraperException
import json

logger = get_logger(__name__)

# Global scheduler instance
scheduler: AsyncIOScheduler = None


async def initialize_scheduler():
    """Initialize and start the APScheduler."""
    global scheduler

    if scheduler and scheduler.running:
        logger.warning("Scheduler is already running")
        return

    scheduler = AsyncIOScheduler()

    # Schedule SEBI scraper to run every 6 hours
    scheduler.add_job(
        run_sebi_scraper,
        "interval",
        hours=6,
        id="sebi_scraper",
        name="SEBI Scraper",
        misfire_grace_time=600,  # Allow 10 min grace period
    )

    try:
        scheduler.start()
        logger.info("Scraper scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        raise


async def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    global scheduler

    if scheduler is None:
        return

    try:
        scheduler.shutdown()
        logger.info("Scraper scheduler shut down")
    except Exception as e:
        logger.error(f"Error shutting down scheduler: {str(e)}")


async def run_sebi_scraper():
    """
    Execute SEBI scraper job.

    Called by scheduler on configured interval.
    """
    job_start_time = datetime.utcnow()
    start_ms = time.time()

    logger.info("Starting SEBI scraper job")

    try:
        # Get database session
        db = next(get_db())

        # Check if job is already running (prevent concurrent execution)
        if is_scraper_running(db, "SEBI"):
            logger.warning("SEBI scraper is already running, skipping")
            return

        # Run the scraper
        scraper = SEBIScraper()
        scraped_regulations = await scraper.fetch()

        logger.info(
            f"SEBI scraper found {len(scraped_regulations)} regulations",
            extra={"count": len(scraped_regulations)},
        )

        # Deduplicate
        new_regulations, dedup_stats = Deduplicator.get_regulations_to_insert(
            scraped_regulations, db
        )

        logger.info(
            f"After deduplication: {len(new_regulations)} new, "
            f"{dedup_stats['duplicates_found']} duplicates",
            extra=dedup_stats,
        )

        # Insert new regulations into database
        inserted_count = 0
        for reg in new_regulations:
            try:
                regulation = Regulation(
                    source_body=reg.source_body,
                    source_url=reg.source_url,
                    original_title=reg.original_title,
                    original_date=reg.original_date,
                    ai_title=reg.original_title,  # Will be updated by AI
                    ai_tldr="",  # Will be filled by AI
                    ai_impact_level="MEDIUM",  # Default, will be updated
                    domains=json.dumps(
                        ["securities"]
                    ),  # Default, will be updated
                    processing_status="pending",
                    content_hash=reg.content_hash,
                    full_text=reg.full_text,
                )
                db.add(regulation)
                inserted_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to insert regulation {reg.original_title[:50]}: {str(e)}",
                    extra={"error": str(e)},
                )
                continue

        db.commit()

        # Record scraper run
        duration_ms = int((time.time() - start_ms) * 1000)
        scraper_run = ScraperRun(
            source_body="SEBI",
            status="success" if inserted_count > 0 else "partial",
            regulations_found=len(scraped_regulations),
            regulations_new=inserted_count,
            regulations_duplicated=dedup_stats["duplicates_found"],
            duration_seconds=int(duration_ms / 1000),
            run_timestamp=job_start_time,
        )
        db.add(scraper_run)
        db.commit()

        logger.info(
            f"SEBI scraper job completed successfully",
            extra={
                "found": len(scraped_regulations),
                "inserted": inserted_count,
                "duplicates": dedup_stats["duplicates_found"],
                "duration_ms": duration_ms,
            },
        )

    except ScraperException as e:
        logger.error(
            f"SEBI scraper failed: {str(e)}",
            extra={"error": str(e)},
        )

        # Record failed run
        try:
            db = next(get_db())
            duration_ms = int((time.time() - start_ms) * 1000)
            scraper_run = ScraperRun(
                source_body="SEBI",
                status="failed",
                regulations_found=0,
                regulations_new=0,
                regulations_duplicated=0,
                duration_seconds=int(duration_ms / 1000),
                run_timestamp=job_start_time,
            )
            db.add(scraper_run)
            db.commit()
        except Exception as db_error:
            logger.error(f"Failed to record scraper run: {str(db_error)}")

    except Exception as e:
        logger.error(
            f"Unexpected error in SEBI scraper job: {str(e)}",
            extra={"error": str(e)},
        )

    finally:
        # Ensure database session is closed
        try:
            if 'db' in locals():
                db.close()
        except:
            pass


def is_scraper_running(db: Session, source_body: str) -> bool:
    """
    Check if a scraper is currently running.

    Prevents concurrent execution of the same scraper.

    Args:
        db: Database session
        source_body: Source body name

    Returns:
        True if scraper is currently running, False otherwise
    """
    try:
        # Get the most recent scraper run
        last_run = (
            db.query(ScraperRun)
            .filter(ScraperRun.source_body == source_body)
            .order_by(ScraperRun.run_timestamp.desc())
            .first()
        )

        if not last_run:
            return False

        # If last run is recent (within 1 minute), consider it still running
        time_since_last_run = datetime.utcnow() - last_run.run_timestamp
        return time_since_last_run.total_seconds() < 60

    except Exception as e:
        logger.error(f"Error checking scraper status: {str(e)}")
        return False


def get_scheduler() -> AsyncIOScheduler:
    """Get the global scheduler instance."""
    return scheduler
