"""
Deduplicator

Prevents duplicate regulations from being inserted into the database.
Uses content hash for fast deduplication.
"""

from typing import List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from src.models import Regulation
from src.scraper.base import ScrapedRegulation
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Deduplicator:
    """
    Deduplicates scraped regulations against database records.

    Uses content hash (SHA256) to detect duplicates efficiently.
    """

    @staticmethod
    def get_regulations_to_insert(
        scraped: List[ScrapedRegulation],
        db: Session,
    ) -> Tuple[List[ScrapedRegulation], Dict[str, Any]]:
        """
        Filter out duplicate regulations.

        Compares scraped regulations against existing database records
        using content hash for fast duplicate detection.

        Args:
            scraped: List of scraped regulations
            db: Database session

        Returns:
            Tuple of (regulations_to_insert, statistics)
            - regulations_to_insert: Filtered list of new regulations
            - statistics: Dict with dedup stats
        """
        if not scraped:
            logger.info("No regulations to process")
            return [], {
                "total_scraped": 0,
                "duplicates_found": 0,
                "new_regulations": 0,
            }

        logger.info(
            f"Deduplicating {len(scraped)} regulations",
            extra={"total": len(scraped)},
        )

        # Get all existing content hashes from database
        existing_hashes = Deduplicator._get_existing_hashes(db)
        logger.debug(
            f"Found {len(existing_hashes)} existing regulations in database",
            extra={"existing_count": len(existing_hashes)},
        )

        # Filter to only new regulations
        new_regulations = []
        duplicates = 0

        for reg in scraped:
            if reg.content_hash in existing_hashes:
                duplicates += 1
                logger.debug(
                    f"Duplicate found: {reg.original_title[:50]}",
                    extra={
                        "hash": reg.content_hash,
                        "title": reg.original_title[:50],
                    },
                )
            else:
                new_regulations.append(reg)

        # Compile statistics
        stats = {
            "total_scraped": len(scraped),
            "duplicates_found": duplicates,
            "new_regulations": len(new_regulations),
            "dedup_rate": (
                (duplicates / len(scraped) * 100) if scraped else 0
            ),
        }

        logger.info(
            f"Deduplication complete: {len(new_regulations)} new, "
            f"{duplicates} duplicates",
            extra=stats,
        )

        return new_regulations, stats

    @staticmethod
    def _get_existing_hashes(db: Session) -> set:
        """
        Get all content hashes of existing regulations.

        Args:
            db: Database session

        Returns:
            Set of existing content hashes
        """
        try:
            hashes = db.query(Regulation.content_hash).all()
            return {h[0] for h in hashes if h[0]}
        except Exception as e:
            logger.error(
                f"Error fetching existing hashes: {str(e)}",
                extra={"error": str(e)},
            )
            return set()

    @staticmethod
    def mark_duplicates(
        all_regulations: List[ScrapedRegulation],
        db: Session,
    ) -> Dict[str, List[ScrapedRegulation]]:
        """
        Mark regulations as duplicates without filtering them.

        Useful for reporting without actually removing regulations.

        Args:
            all_regulations: List of all scraped regulations
            db: Database session

        Returns:
            Dict with 'new' and 'duplicate' keys
        """
        existing_hashes = Deduplicator._get_existing_hashes(db)

        new = []
        duplicates = []

        for reg in all_regulations:
            if reg.content_hash in existing_hashes:
                duplicates.append(reg)
            else:
                new.append(reg)

        return {"new": new, "duplicates": duplicates}
