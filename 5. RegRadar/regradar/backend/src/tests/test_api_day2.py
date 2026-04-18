"""
Day 2 API Tests

Comprehensive tests for all FastAPI endpoints including:
- Regulations listing and filtering
- Session management
- Statistics
- Domain information
"""

import pytest
import json
from datetime import datetime
from sqlalchemy.orm import Session
from src.models import Regulation, UserPreference


@pytest.fixture
def test_regulation(db: Session):
    """Create a test regulation."""
    reg = Regulation(
        source_body="SEBI",
        source_url="https://example.com/sebi/1",
        original_title="SEBI Circular 2026",
        original_date=datetime.utcnow(),
        ai_title="SEBI Circular Summary",
        ai_tldr="This is a test SEBI circular",
        ai_impact_level="HIGH",
        domains=json.dumps(["securities", "banking"]),
        processing_status="processed",
        ai_what_changed="Changed regulations",
        ai_who_affected="Brokers and dealers",
        ai_action_required="Review compliance policies",
        content_hash="abc123",
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


@pytest.fixture
def test_regulations(db: Session):
    """Create multiple test regulations."""
    regs = []
    for i in range(5):
        reg = Regulation(
            source_body="SEBI" if i % 2 == 0 else "RBI",
            source_url=f"https://example.com/reg/{i}",
            original_title=f"Regulation {i}",
            original_date=datetime.utcnow(),
            ai_title=f"Regulation {i} Summary",
            ai_tldr=f"This is regulation {i}",
            ai_impact_level="HIGH" if i % 2 == 0 else "MEDIUM",
            domains=json.dumps(["securities"] if i % 2 == 0 else ["banking"]),
            processing_status="processed",
            content_hash=f"hash{i}",
        )
        db.add(reg)
        regs.append(reg)
    db.commit()
    return regs


class TestListRegulations:
    """Test GET /api/regulations endpoint."""

    def test_list_regulations_success(self, test_client, test_regulations):
        """Test listing regulations successfully."""
        response = test_client.get("/api/regulations")
        assert response.status_code == 200
        data = response.json()
        assert "regulations" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "has_more" in data
        assert len(data["regulations"]) == 5

    def test_list_regulations_with_limit(self, test_regulations, test_client):
        """Test listing with limit parameter."""
        response = test_client.get("/api/regulations?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["regulations"]) == 2
        assert data["has_more"] is True

    def test_list_regulations_with_offset(self, test_regulations, test_client):
        """Test listing with offset parameter."""
        response = test_client.get("/api/regulations?offset=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["regulations"]) == 2
        assert data["page"] == 2

    def test_list_regulations_with_source_filter(self, test_regulations, test_client):
        """Test listing with source filter."""
        response = test_client.get("/api/regulations?source=SEBI")
        assert response.status_code == 200
        data = response.json()
        for reg in data["regulations"]:
            assert reg["source_body"] == "SEBI"

    def test_list_regulations_with_impact_filter(self, test_regulations, test_client):
        """Test listing with impact level filter."""
        response = test_client.get("/api/regulations?impact=HIGH")
        assert response.status_code == 200
        data = response.json()
        for reg in data["regulations"]:
            assert reg["ai_impact_level"] == "HIGH"

    def test_list_regulations_invalid_limit(self, test_client):
        """Test listing with invalid limit."""
        response = test_client.get("/api/regulations?limit=101")
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error_code" in data or "detail" in data

    def test_list_regulations_negative_offset(self, test_client):
        """Test listing with negative offset."""
        response = test_client.get("/api/regulations?offset=-1")
        assert response.status_code in [400, 422]

    def test_list_regulations_empty(self, test_client):
        """Test listing with no regulations."""
        response = test_client.get("/api/regulations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["regulations"]) == 0


class TestGetRegulation:
    """Test GET /api/regulations/{id} endpoint."""

    def test_get_regulation_success(self, test_regulation, test_client):
        """Test getting a regulation successfully."""
        response = test_client.get(f"/api/regulations/{test_regulation.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_regulation.id
        assert data["source_body"] == "SEBI"
        assert data["original_title"] == "SEBI Circular 2026"

    def test_get_regulation_not_found(self, test_client):
        """Test getting a non-existent regulation."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_get_regulation_fields(self, test_regulation, test_client):
        """Test that response includes all required fields."""
        response = test_client.get(f"/api/regulations/{test_regulation.id}")
        assert response.status_code == 200
        data = response.json()
        required_fields = [
            "id",
            "source_body",
            "original_title",
            "original_date",
            "source_url",
            "ai_title",
            "ai_tldr",
            "ai_impact_level",
            "domains",
            "processing_status",
            "created_at",
            "updated_at",
        ]
        for field in required_fields:
            assert field in data


class TestListDomains:
    """Test GET /api/domains endpoint."""

    def test_list_domains_success(self, test_regulations, test_client):
        """Test listing domains successfully."""
        response = test_client.get("/api/domains")
        assert response.status_code == 200
        data = response.json()
        assert "domains" in data
        assert isinstance(data["domains"], list)
        # Should have securities and banking
        domain_names = [d["name"] for d in data["domains"]]
        assert "securities" in domain_names
        assert "banking" in domain_names

    def test_list_domains_with_counts(self, test_regulations, test_client):
        """Test that domains include correct counts."""
        response = test_client.get("/api/domains")
        assert response.status_code == 200
        data = response.json()
        for domain in data["domains"]:
            assert "name" in domain
            assert "count" in domain
            assert domain["count"] > 0

    def test_list_domains_empty(self, test_client):
        """Test listing domains with no regulations."""
        response = test_client.get("/api/domains")
        assert response.status_code == 200
        data = response.json()
        assert data["domains"] == []


class TestGetStats:
    """Test GET /api/stats endpoint."""

    def test_get_stats_success(self, test_regulations, test_client):
        """Test getting stats successfully."""
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_regulations" in data
        assert "by_source" in data
        assert "by_impact" in data
        assert "by_domain" in data
        assert "last_updated" in data
        assert data["total_regulations"] == 5

    def test_get_stats_by_source(self, test_regulations, test_client):
        """Test stats broken down by source."""
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        # Should have SEBI and RBI
        assert "SEBI" in data["by_source"]
        assert "RBI" in data["by_source"]
        # 5 regulations, so 3 of one and 2 of other
        assert sum(data["by_source"].values()) == 5

    def test_get_stats_by_impact(self, test_regulations, test_client):
        """Test stats broken down by impact."""
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        # Should have HIGH and MEDIUM
        assert "HIGH" in data["by_impact"]
        assert "MEDIUM" in data["by_impact"]

    def test_get_stats_by_domain(self, test_regulations, test_client):
        """Test stats broken down by domain."""
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "securities" in data["by_domain"]
        assert "banking" in data["by_domain"]

    def test_get_stats_empty(self, test_client):
        """Test stats with no regulations."""
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_regulations"] == 0
        assert data["by_source"] == {}


class TestSessionManagement:
    """Test session creation and management."""

    def test_create_session_success(self, test_client):
        """Test creating a session successfully."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["securities", "banking"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert len(data["session_id"]) > 0
        assert data["domains"] == ["securities", "banking"]
        assert "created_at" in data
        assert "last_accessed" in data

    def test_create_session_empty_domains(self, test_client):
        """Test creating a session with no domains."""
        response = test_client.post(
            "/api/session",
            json={"domains": []},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["domains"] == []

    def test_create_session_invalid_domain(self, test_client):
        """Test creating a session with invalid domain."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["invalid_domain"]},
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_get_session_success(self, test_client):
        """Test getting a session."""
        # Create session first
        create_resp = test_client.post(
            "/api/session",
            json={"domains": ["securities"]},
        )
        session_id = create_resp.json()["session_id"]

        # Get session
        response = test_client.get(f"/api/session/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["domains"] == ["securities"]

    def test_get_session_not_found(self, test_client):
        """Test getting a non-existent session."""
        response = test_client.get("/api/session/nonexistent")
        assert response.status_code == 404

    def test_update_session_success(self, test_client):
        """Test updating a session."""
        # Create session
        create_resp = test_client.post(
            "/api/session",
            json={"domains": ["securities"]},
        )
        session_id = create_resp.json()["session_id"]

        # Update session
        response = test_client.put(
            f"/api/session/{session_id}",
            json={"domains": ["banking", "insurance"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["domains"] == ["banking", "insurance"]

    def test_update_session_not_found(self, test_client):
        """Test updating a non-existent session."""
        response = test_client.put(
            "/api/session/nonexistent",
            json={"domains": ["banking"]},
        )
        assert response.status_code == 404


class TestScraperRuns:
    """Test GET /api/scraper-runs endpoint."""

    def test_get_scraper_runs_empty(self, test_client):
        """Test getting scraper runs when none exist."""
        response = test_client.get("/api/scraper-runs")
        assert response.status_code == 200
        data = response.json()
        assert data["runs"] == []
        assert data["total"] == 0

    def test_get_scraper_runs_with_pagination(self, db: Session, test_client):
        """Test scraper runs pagination."""
        from src.models import ScraperRun

        # Create multiple scraper runs
        for i in range(5):
            run = ScraperRun(
                source_body="SEBI",
                status="success",
                regulations_found=10,
                regulations_new=5,
                regulations_duplicated=5,
                duration_seconds=60,
            )
            db.add(run)
        db.commit()

        response = test_client.get("/api/scraper-runs?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["runs"]) == 2
        assert data["total"] == 5
        assert data["has_more"] is True


class TestHealthAndRoot:
    """Test health check and root endpoints."""

    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "database" in data
        assert "environment" in data
        assert "response_time_ms" in data
        assert data["status"] in ["ok", "degraded"]

    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "RegRadar API"
        assert "docs_url" in data
        assert "health_url" in data


class TestCorrelationHeaders:
    """Test correlation ID header handling."""

    def test_correlation_id_in_response(self, test_client):
        """Test that correlation ID is in response."""
        response = test_client.get("/health")
        assert "X-Correlation-ID" in response.headers

    def test_correlation_id_preserved(self, test_client):
        """Test that provided correlation ID is preserved."""
        correlation_id = "test-correlation-123"
        response = test_client.get(
            "/health",
            headers={"X-Correlation-ID": correlation_id},
        )
        assert response.headers["X-Correlation-ID"] == correlation_id


class TestSecurityHeaders:
    """Test security headers in responses."""

    def test_xss_protection_header(self, test_client):
        """Test XSS protection header."""
        response = test_client.get("/health")
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_content_type_header(self, test_client):
        """Test content type header."""
        response = test_client.get("/health")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_hsts_header(self, test_client):
        """Test HSTS header."""
        response = test_client.get("/health")
        assert "Strict-Transport-Security" in response.headers


class TestErrorResponses:
    """Test error response formatting."""

    def test_not_found_error_format(self, test_client):
        """Test 404 error response format."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert "error_code" in data
        assert "status_code" in data
        assert "details" in data

    def test_validation_error_format(self, test_client):
        """Test validation error response format."""
        response = test_client.get("/api/regulations?limit=999")
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data or "detail" in data

    def test_error_includes_correlation_id(self, test_client):
        """Test that errors include correlation ID."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        # Correlation ID may be in response or header
        assert "correlation_id" in data or "X-Correlation-ID" in response.headers
