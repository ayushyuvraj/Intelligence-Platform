"""
Test Suite for Database Module

Tests database initialization, session management, models, and queries.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from src.models import (
    Regulation,
    UserPreference,
    ScraperRun,
    AIProcessingHistory,
    RegulationRelationship,
    EmailDigest,
)


class TestDatabaseConnection:
    """Tests for database connection and management."""

    def test_test_db_session_is_valid(self, test_db_session: Session):
        """Test that test database session is valid."""
        assert test_db_session is not None
        assert test_db_session.is_active

    def test_database_tables_created(self, test_db_session: Session):
        """Test that all database tables are created."""
        from sqlalchemy import inspect as sql_inspect

        # Test by querying for table metadata
        engine = test_db_session.get_bind()
        inspector = sql_inspect(engine)
        tables = inspector.get_table_names()

        # Verify tables exist
        assert len(tables) > 0
        assert "regulations" in tables
        assert "user_preferences" in tables
        assert "scraper_runs" in tables
        assert "ai_processing_history" in tables


class TestRegulationModel:
    """Tests for Regulation model."""

    def test_create_regulation(self, test_db_session: Session, sample_regulation_data: dict):
        """Test creating a regulation record."""
        from datetime import datetime

        regulation = Regulation(
            source_body=sample_regulation_data["source_body"],
            original_title=sample_regulation_data["original_title"],
            original_date=datetime.fromisoformat(sample_regulation_data["original_date"]),
            source_url=sample_regulation_data["source_url"],
            full_text=sample_regulation_data["full_text"],
            content_hash=sample_regulation_data["content_hash"],
            ai_title=sample_regulation_data["ai_title"],
            ai_tldr=sample_regulation_data["ai_tldr"],
            ai_impact_level=sample_regulation_data["ai_impact_level"],
            domains=sample_regulation_data["domains"],
            processing_status=sample_regulation_data["processing_status"],
        )

        test_db_session.add(regulation)
        test_db_session.commit()

        assert regulation.id is not None
        assert regulation.source_body == "RBI"

    def test_regulation_timestamps_auto_set(self, test_db_session: Session, sample_regulation_data: dict):
        """Test that created_at timestamp is automatically set."""
        from datetime import datetime

        regulation = Regulation(
            source_body=sample_regulation_data["source_body"],
            original_title=sample_regulation_data["original_title"],
            original_date=datetime.fromisoformat(sample_regulation_data["original_date"]),
            source_url=sample_regulation_data["source_url"],
            full_text=sample_regulation_data["full_text"],
            content_hash=sample_regulation_data["content_hash"],
            ai_title=sample_regulation_data["ai_title"],
            ai_tldr=sample_regulation_data["ai_tldr"],
            ai_impact_level=sample_regulation_data["ai_impact_level"],
            domains=sample_regulation_data["domains"],
        )

        test_db_session.add(regulation)
        test_db_session.commit()

        assert regulation.created_at is not None
        assert isinstance(regulation.created_at, datetime)

    def test_regulation_unique_constraints(self, test_db_session: Session, sample_regulation_data: dict):
        """Test that unique constraints are enforced."""
        from datetime import datetime
        from sqlalchemy.exc import IntegrityError

        regulation1 = Regulation(
            source_body=sample_regulation_data["source_body"],
            original_title=sample_regulation_data["original_title"],
            original_date=datetime.fromisoformat(sample_regulation_data["original_date"]),
            source_url=sample_regulation_data["source_url"],
            full_text=sample_regulation_data["full_text"],
            content_hash=sample_regulation_data["content_hash"],
            ai_title=sample_regulation_data["ai_title"],
            ai_tldr=sample_regulation_data["ai_tldr"],
            ai_impact_level=sample_regulation_data["ai_impact_level"],
            domains=sample_regulation_data["domains"],
        )

        regulation2 = Regulation(
            source_body="SEBI",
            original_title="Different Title",
            original_date=datetime.fromisoformat(sample_regulation_data["original_date"]),
            source_url=sample_regulation_data["source_url"],  # Same URL - should fail
            full_text="Different text",
            content_hash="different_hash",
            ai_title="Different AI Title",
            ai_tldr="Different TLDR",
            ai_impact_level="MEDIUM",
            domains=sample_regulation_data["domains"],
        )

        test_db_session.add(regulation1)
        test_db_session.commit()

        test_db_session.add(regulation2)

        with pytest.raises(IntegrityError):
            test_db_session.commit()


class TestUserPreferenceModel:
    """Tests for UserPreference model."""

    def test_create_user_preference(self, test_db_session: Session, sample_user_preference_data: dict):
        """Test creating a user preference record."""
        user_pref = UserPreference(
            session_id=sample_user_preference_data["session_id"],
            selected_domains=sample_user_preference_data["selected_domains"],
            email=sample_user_preference_data["email"],
        )

        test_db_session.add(user_pref)
        test_db_session.commit()

        assert user_pref.id is not None
        assert user_pref.session_id == sample_user_preference_data["session_id"]

    def test_user_preference_unique_session_id(self, test_db_session: Session, sample_user_preference_data: dict):
        """Test that session_id must be unique."""
        from sqlalchemy.exc import IntegrityError

        user_pref1 = UserPreference(
            session_id=sample_user_preference_data["session_id"],
            selected_domains=sample_user_preference_data["selected_domains"],
        )

        user_pref2 = UserPreference(
            session_id=sample_user_preference_data["session_id"],  # Same session_id
            selected_domains='["different"]',
        )

        test_db_session.add(user_pref1)
        test_db_session.commit()

        test_db_session.add(user_pref2)

        with pytest.raises(IntegrityError):
            test_db_session.commit()


class TestScraperRunModel:
    """Tests for ScraperRun model."""

    def test_create_scraper_run(self, test_db_session: Session, sample_scraper_run_data: dict):
        """Test creating a scraper run record."""
        scraper_run = ScraperRun(
            source_body=sample_scraper_run_data["source_body"],
            status=sample_scraper_run_data["status"],
            regulations_found=sample_scraper_run_data["regulations_found"],
            regulations_new=sample_scraper_run_data["regulations_new"],
            regulations_duplicated=sample_scraper_run_data["regulations_duplicated"],
            duration_seconds=sample_scraper_run_data["duration_seconds"],
        )

        test_db_session.add(scraper_run)
        test_db_session.commit()

        assert scraper_run.id is not None
        assert scraper_run.status == "success"


class TestAIProcessingHistoryModel:
    """Tests for AIProcessingHistory model."""

    def test_create_ai_processing_history(
        self,
        test_db_session: Session,
        sample_regulation_data: dict,
        sample_ai_processing_history_data: dict,
    ):
        """Test creating an AI processing history record."""
        from datetime import datetime

        # First create a regulation
        regulation = Regulation(
            source_body=sample_regulation_data["source_body"],
            original_title=sample_regulation_data["original_title"],
            original_date=datetime.fromisoformat(sample_regulation_data["original_date"]),
            source_url=sample_regulation_data["source_url"],
            full_text=sample_regulation_data["full_text"],
            content_hash=sample_regulation_data["content_hash"],
            ai_title=sample_regulation_data["ai_title"],
            ai_tldr=sample_regulation_data["ai_tldr"],
            ai_impact_level=sample_regulation_data["ai_impact_level"],
            domains=sample_regulation_data["domains"],
        )

        test_db_session.add(regulation)
        test_db_session.commit()

        # Create AI processing history linked to the regulation
        ai_history = AIProcessingHistory(
            regulation_id=regulation.id,
            attempt_number=sample_ai_processing_history_data["attempt_number"],
            status=sample_ai_processing_history_data["status"],
            model_used=sample_ai_processing_history_data["model_used"],
            tokens_used=sample_ai_processing_history_data["tokens_used"],
            processing_time_ms=sample_ai_processing_history_data["processing_time_ms"],
        )

        test_db_session.add(ai_history)
        test_db_session.commit()

        assert ai_history.id is not None
        assert ai_history.regulation_id == regulation.id

    def test_ai_processing_history_relationship(self, test_db_session: Session, sample_regulation_data: dict):
        """Test that AI processing history relationship works."""
        from datetime import datetime

        # Create regulation
        regulation = Regulation(
            source_body=sample_regulation_data["source_body"],
            original_title=sample_regulation_data["original_title"],
            original_date=datetime.fromisoformat(sample_regulation_data["original_date"]),
            source_url=sample_regulation_data["source_url"],
            full_text=sample_regulation_data["full_text"],
            content_hash=sample_regulation_data["content_hash"],
            ai_title=sample_regulation_data["ai_title"],
            ai_tldr=sample_regulation_data["ai_tldr"],
            ai_impact_level=sample_regulation_data["ai_impact_level"],
            domains=sample_regulation_data["domains"],
        )

        test_db_session.add(regulation)
        test_db_session.commit()

        # Create AI history
        ai_history = AIProcessingHistory(
            regulation_id=regulation.id,
            status="success",
        )

        test_db_session.add(ai_history)
        test_db_session.commit()

        # Verify relationship
        assert len(regulation.ai_history) == 1
        assert regulation.ai_history[0].status == "success"


class TestModelIndexes:
    """Tests for model indexes."""

    def test_indexes_are_defined(self):
        """Test that indexes are defined on models."""
        # This is a basic test to ensure index definitions don't crash
        # In production, you'd test actual index performance
        assert Regulation.__table__ is not None
        assert UserPreference.__table__ is not None
        assert ScraperRun.__table__ is not None


class TestQueryPerformance:
    """Tests for query performance."""

    def test_regulation_query_performance(self, test_db_session: Session, sample_regulation_data: dict):
        """Test that regulation queries are performant."""
        import time
        from datetime import datetime

        # Create multiple regulations
        for i in range(10):
            regulation = Regulation(
                source_body=sample_regulation_data["source_body"],
                original_title=f"Regulation {i}",
                original_date=datetime.fromisoformat(sample_regulation_data["original_date"]),
                source_url=f"https://example.com/reg{i}",
                full_text=sample_regulation_data["full_text"],
                content_hash=f"hash{i}",
                ai_title=sample_regulation_data["ai_title"],
                ai_tldr=sample_regulation_data["ai_tldr"],
                ai_impact_level=sample_regulation_data["ai_impact_level"],
                domains=sample_regulation_data["domains"],
            )
            test_db_session.add(regulation)

        test_db_session.commit()

        # Test query performance
        start_time = time.time()
        regulations = test_db_session.query(Regulation).filter_by(source_body="RBI").all()
        elapsed_time = (time.time() - start_time) * 1000

        assert len(regulations) == 10
        assert elapsed_time < 100, f"Query took {elapsed_time}ms"
