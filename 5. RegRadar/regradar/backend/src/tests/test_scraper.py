"""
Scraper Tests

Tests for SEBI scraper, base scraper, and deduplication logic.
"""

import pytest
import asyncio
from datetime import datetime
import json
from sqlalchemy.orm import Session

from src.scraper.sebi import SEBIScraper
from src.scraper.base import ScrapedRegulation
from src.scraper.deduplicator import Deduplicator
from src.models import Regulation


class TestSEBIScraper:
    """Test SEBI scraper."""

    def test_sebi_scraper_initialization(self):
        """Test SEBI scraper initialization."""
        scraper = SEBIScraper()
        assert scraper.source_body == "SEBI"
        assert scraper.base_url == "https://www.sebi.gov.in"
        assert scraper.timeout_seconds == 30
        assert scraper.max_retries == 2


class TestDeduplicator:
    """Test deduplication logic."""

    def test_no_duplicates(self, db: Session):
        """Test with no existing regulations."""
        scraped = [
            ScrapedRegulation(
                source_body="SEBI",
                source_url="https://example.com/1",
                original_title="Regulation 1",
                original_date=datetime.utcnow(),
                content_hash="abc123",
            ),
            ScrapedRegulation(
                source_body="SEBI",
                source_url="https://example.com/2",
                original_title="Regulation 2",
                original_date=datetime.utcnow(),
                content_hash="def456",
            ),
        ]

        new_regs, stats = Deduplicator.get_regulations_to_insert(scraped, db)

        assert len(new_regs) == 2
        assert stats["duplicates_found"] == 0
        assert stats["new_regulations"] == 2
        assert stats["total_scraped"] == 2

    def test_with_duplicates(self, db: Session):
        """Test with existing regulations."""
        # Add existing regulation
        existing = Regulation(
            source_body="SEBI",
            source_url="https://example.com/1",
            original_title="Existing Regulation",
            original_date=datetime.utcnow(),
            ai_title="Existing",
            ai_tldr="Summary",
            ai_impact_level="MEDIUM",
            domains=json.dumps(["securities"]),
            processing_status="processed",
            content_hash="abc123",
        )
        db.add(existing)
        db.commit()

        # Try to insert both new and duplicate
        scraped = [
            ScrapedRegulation(
                source_body="SEBI",
                source_url="https://example.com/1",
                original_title="Existing Regulation",
                original_date=datetime.utcnow(),
                content_hash="abc123",  # This is a duplicate
            ),
            ScrapedRegulation(
                source_body="SEBI",
                source_url="https://example.com/2",
                original_title="New Regulation",
                original_date=datetime.utcnow(),
                content_hash="def456",  # This is new
            ),
        ]

        new_regs, stats = Deduplicator.get_regulations_to_insert(scraped, db)

        assert len(new_regs) == 1
        assert new_regs[0].original_title == "New Regulation"
        assert stats["duplicates_found"] == 1
        assert stats["new_regulations"] == 1

    def test_empty_input(self, db: Session):
        """Test with empty input."""
        new_regs, stats = Deduplicator.get_regulations_to_insert([], db)

        assert len(new_regs) == 0
        assert stats["total_scraped"] == 0
        assert stats["duplicates_found"] == 0
        assert stats["new_regulations"] == 0

    def test_mark_duplicates(self, db: Session):
        """Test marking duplicates without filtering."""
        # Add existing regulation
        existing = Regulation(
            source_body="SEBI",
            source_url="https://example.com/1",
            original_title="Existing",
            original_date=datetime.utcnow(),
            ai_title="Existing",
            ai_tldr="Summary",
            ai_impact_level="MEDIUM",
            domains=json.dumps(["securities"]),
            processing_status="processed",
            content_hash="hash1",
        )
        db.add(existing)
        db.commit()

        scraped = [
            ScrapedRegulation(
                source_body="SEBI",
                source_url="https://example.com/1",
                original_title="Existing",
                original_date=datetime.utcnow(),
                content_hash="hash1",
            ),
            ScrapedRegulation(
                source_body="SEBI",
                source_url="https://example.com/2",
                original_title="New",
                original_date=datetime.utcnow(),
                content_hash="hash2",
            ),
        ]

        result = Deduplicator.mark_duplicates(scraped, db)

        assert len(result["new"]) == 1
        assert len(result["duplicates"]) == 1
        assert result["new"][0].original_title == "New"
        assert result["duplicates"][0].original_title == "Existing"


class TestScrapedRegulation:
    """Test ScrapedRegulation data class."""

    def test_creation(self):
        """Test ScrapedRegulation creation."""
        reg = ScrapedRegulation(
            source_body="SEBI",
            source_url="https://example.com",
            original_title="Test Regulation",
            original_date=datetime.utcnow(),
            full_text="Some text",
            content_hash="abc123",
        )

        assert reg.source_body == "SEBI"
        assert reg.source_url == "https://example.com"
        assert reg.original_title == "Test Regulation"
        assert reg.full_text == "Some text"
        assert reg.content_hash == "abc123"

    def test_optional_fields(self):
        """Test ScrapedRegulation with optional fields."""
        reg = ScrapedRegulation(
            source_body="RBI",
            source_url="https://rbi.org.in",
            original_title="RBI Circular",
            original_date=datetime.utcnow(),
        )

        assert reg.full_text is None
        assert reg.content_hash is None
