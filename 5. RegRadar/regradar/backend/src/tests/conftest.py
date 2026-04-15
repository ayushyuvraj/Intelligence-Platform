"""
Pytest Configuration and Fixtures

Provides reusable fixtures for testing:
- In-memory SQLite database
- FastAPI test client
- Database session
- Sample data factories
"""

import pytest
import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set up test environment variables BEFORE importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["API_HOST"] = "localhost"
os.environ["API_PORT"] = "8000"
os.environ["BACKEND_URL"] = "http://localhost:8000"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["DEBUG"] = "true"
os.environ["GEMINI_API_KEY"] = "test-key-for-testing-only"
os.environ["LOG_LEVEL"] = "INFO"

from fastapi.testclient import TestClient
from src.main import app
from src.models import Base
from src.database import DatabaseManager, get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Session:
    """Create a database session for testing."""
    TestingSessionLocal = sessionmaker(bind=test_db_engine, expire_on_commit=False)
    session = TestingSessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def test_client(test_db_session: Session) -> TestClient:
    """Create a FastAPI test client with test database."""

    # Override the get_db dependency to use test database
    def override_get_db():
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create test client with proper base_url to pass TrustedHostMiddleware
    client = TestClient(app, base_url="http://localhost:8000")

    yield client

    # Reset overrides
    app.dependency_overrides.clear()


# Alias for easier use in tests
@pytest.fixture(scope="function")
def db(test_db_session: Session) -> Session:
    """Alias for test_db_session."""
    return test_db_session


@pytest.fixture
def sample_regulation_data() -> dict:
    """Sample regulation data for testing."""
    return {
        "source_body": "RBI",
        "original_title": "Test Notification on Interest Rates",
        "original_date": "2024-01-15",
        "source_url": "https://rbi.org.in/test",
        "full_text": "Full text of the regulation goes here.",
        "content_hash": "abc123def456",
        "ai_title": "RBI Updates Interest Rate Guidelines",
        "ai_tldr": "The RBI has updated interest rate guidelines effective immediately.",
        "ai_what_changed": "Interest rate bands have been adjusted.",
        "ai_who_affected": "All banks and financial institutions",
        "ai_action_required": "Review rate cards and communicate to customers",
        "ai_impact_level": "HIGH",
        "domains": '["banking", "monetary_policy"]',
        "processing_status": "processed",
    }


@pytest.fixture
def sample_user_preference_data() -> dict:
    """Sample user preference data for testing."""
    return {
        "session_id": "test_session_123456",
        "selected_domains": '["banking", "securities"]',
        "email": "test@example.com",
    }


@pytest.fixture
def sample_scraper_run_data() -> dict:
    """Sample scraper run data for testing."""
    return {
        "source_body": "RBI",
        "status": "success",
        "regulations_found": 5,
        "regulations_new": 3,
        "regulations_duplicated": 2,
        "duration_seconds": 30,
    }


@pytest.fixture
def sample_ai_processing_history_data() -> dict:
    """Sample AI processing history data for testing."""
    return {
        "attempt_number": 1,
        "status": "success",
        "model_used": "gemini-2.0-flash",
        "tokens_used": 450,
        "processing_time_ms": 2500,
    }
