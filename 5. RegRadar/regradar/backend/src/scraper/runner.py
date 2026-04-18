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
from src.scraper.rbi import RBIScraper
from src.scraper.deduplicator import Deduplicator
from src.ai.engine import GeminiEngine
from src.models import Regulation, ScraperRun
from src.utils.logger import get_logger
from src.utils.errors import ScraperException
import json

logger = get_logger(__name__)

# Global scheduler instance
scheduler: AsyncIOScheduler = None


async def run_ai_processing():
    """
    Process all 'pending' regulations using the AI Engine.
    Uses database transactions to prevent race conditions.
    """
    job_start_time = datetime.utcnow()
    start_ms = time.time()

    logger.info("Starting AI processing job")

    try:
        db = next(get_db())
        engine = GeminiEngine()

        # Find all pending regulations (not currently processing)
        pending_regs = db.query(Regulation).filter(
            Regulation.processing_status == "pending"
        ).all()

        if not pending_regs:
            logger.info("No pending regulations to process")
            return

        processed_count = 0
        failed_count = 0

        for reg in pending_regs:
            try:
                # Mark as processing before analysis (atomic update to prevent race condition)
                db.query(Regulation).filter(Regulation.id == reg.id).update(
                    {Regulation.processing_status: "processing"},
                    synchronize_session=False
                )
                db.commit()

                # Analyze text
                analysis = await engine.analyze_regulation(reg.full_text)

                # Fetch fresh copy after potential concurrent updates
                reg = db.query(Regulation).filter(Regulation.id == reg.id).first()
                if not reg:
                    logger.warning(f"Regulation {reg.id} was deleted during processing")
                    failed_count += 1
                    continue

                # Update regulation record with analysis results
                reg.ai_title = analysis.ai_title
                reg.ai_tldr = analysis.ai_tldr
                reg.ai_what_changed = analysis.ai_what_changed
                reg.ai_who_affected = ", ".join(analysis.ai_who_affected)
                reg.ai_action_required = "\n".join(analysis.ai_action_required)
                reg.ai_impact_level = analysis.ai_impact_level
                reg.domains = json.dumps(analysis.domains)
                reg.processing_status = "completed"

                # Log to history
                history = AIProcessingHistory(
                    regulation_id=reg.id,
                    processing_date=job_start_time,
                    status="success",
                    tokens_used=0 # Placeholder
                )
                db.add(history)
                db.commit()

                processed_count += 1
            except Exception as e:
                logger.error(f"AI analysis failed for reg {reg.id}: {str(e)}")
                # Mark as review_pending if analysis fails
                try:
                    db.query(Regulation).filter(Regulation.id == reg.id).update(
                        {Regulation.processing_status: "review_pending"},
                        synchronize_session=False
                    )
                    db.commit()
                except Exception as update_error:
                    logger.error(f"Failed to update status for reg {reg.id}: {str(update_error)}")
                    db.rollback()
                failed_count += 1

        duration_ms = int((time.time() - start_ms) * 1000)
        logger.info(
            "AI processing job completed",
            extra={
                "processed": processed_count,
                "failed": failed_count,
                "duration_ms": duration_ms
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error in AI processing job: {str(e)}")
    finally:
        try:
            if 'db' in locals():
                db.close()
        except:
            pass

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

    # Schedule RBI scraper to run every 6 hours
    scheduler.add_job(
        run_rbi_scraper,
        "interval",
        hours=6,
        id="rbi_scraper",
        name="RBI Scraper",
        misfire_grace_time=600,
    )

    # Schedule AI processing to run every hour
    scheduler.add_job(
        run_ai_processing,
        "interval",
        hours=1,
        id="ai_processor",
        name="AI Engine Processor",
        misfire_grace_time=600,
    )

    try:
        scheduler.start()
        logger.info("Scraper and AI scheduler started")
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

async def run_rbi_scraper():
    """
    Execute RBI scraper job.
    """
    job_start_time = datetime.utcnow()
    start_ms = time.time()

    logger.info("Starting RBI scraper job")

    try:
        # Get database session
        db = next(get_db())

        # Check if job is already running
        if is_scraper_running(db, "RBI"):
            logger.warning("RBI scraper is already running, skipping")
            return

        # Run the scraper
        scraper = RBIScraper()
        scraped_regulations = await scraper.fetch()

        logger.info(
            f"RBI scraper found {len(scraped_regulations)} regulations",
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
                    ai_title=reg.original_title,
                    ai_tldr="",
                    ai_impact_level="MEDIUM",
                    domains=json.dumps(["finance"]), # Default for RBI
                    processing_status="pending",
                    content_hash=reg.content_hash,
                    full_text=reg.full_text,
                )
                db.add(regulation)
                inserted_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to insert RBI regulation {reg.original_title[:50]}: {str(e)}",
                    extra={"error": str(e)},
                )
                continue

        db.commit()

        # Record scraper run
        duration_ms = int((time.time() - start_ms) * 1000)
        scraper_run = ScraperRun(
            source_body="RBI",
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
            f"RBI scraper job completed successfully",
            extra={
                "found": len(scraped_regulations),
                "inserted": inserted_count,
                "duplicates": dedup_stats["duplicates_found"],
                "duration_ms": duration_ms,
            },
        )

    except ScraperException as e:
        logger.error(
            f"RBI scraper failed: {str(e)}",
            extra={"error": str(e)},
        )
        try:
            db = next(get_db())
            duration_ms = int((time.time() - start_ms) * 1000)
            scraper_run = ScraperRun(
                source_body="RBI",
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
            logger.error(f"Failed to record RBI scraper run: {str(db_error)}")

    except Exception as e:
        logger.error(f"Unexpected error in RBI scraper job: {str(e)}")

    finally:
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
