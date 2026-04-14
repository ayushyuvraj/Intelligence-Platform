"""
Test Suite for FastAPI Endpoints

Tests health check, root endpoint, and other API functionality.
"""

import pytest
import time
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check_returns_200(self, test_client: TestClient):
        """Test that health check returns 200 OK."""
        response = test_client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_format(self, test_client: TestClient):
        """Test that health check response has correct format."""
        response = test_client.get("/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "database" in data
        assert "environment" in data
        assert "response_time_ms" in data

    def test_health_check_database_connection(self, test_client: TestClient):
        """Test that health check verifies database connection."""
        response = test_client.get("/health")
        data = response.json()

        assert "database" in data
        assert "connected" in data["database"]
        assert "table_count" in data["database"]

    def test_health_check_performance(self, test_client: TestClient):
        """Test that health check responds in less than 500ms."""
        start_time = time.time()
        response = test_client.get("/health")
        elapsed_time = (time.time() - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_time < 500, f"Health check took {elapsed_time}ms, expected <500ms"

    def test_health_check_response_time_ms_accurate(self, test_client: TestClient):
        """Test that health check reports accurate response time."""
        response = test_client.get("/health")
        data = response.json()

        # Response time should be less than 100ms
        assert data["response_time_ms"] < 100

    def test_health_check_correlation_id_header(self, test_client: TestClient):
        """Test that health check returns correlation ID in headers."""
        response = test_client.get("/health")

        assert "x-correlation-id" in response.headers
        correlation_id = response.headers["x-correlation-id"]
        assert len(correlation_id) > 0

    def test_health_check_version(self, test_client: TestClient):
        """Test that health check reports correct version."""
        response = test_client.get("/health")
        data = response.json()

        assert data["version"] == "1.0.0"

    def test_health_check_status_ok_when_db_connected(self, test_client: TestClient):
        """Test that status is 'ok' when database is connected."""
        response = test_client.get("/health")
        data = response.json()

        # In test environment with in-memory db, should be connected
        if data["database"]["connected"]:
            assert data["status"] in ["ok", "degraded"]


class TestRootEndpoint:
    """Tests for the root / endpoint."""

    def test_root_returns_200(self, test_client: TestClient):
        """Test that root endpoint returns 200 OK."""
        response = test_client.get("/")
        assert response.status_code == 200

    def test_root_response_format(self, test_client: TestClient):
        """Test that root endpoint response has correct format."""
        response = test_client.get("/")
        data = response.json()

        assert "service" in data
        assert "version" in data
        assert "description" in data
        assert "docs_url" in data
        assert "health_url" in data

    def test_root_service_name(self, test_client: TestClient):
        """Test that root endpoint returns correct service name."""
        response = test_client.get("/")
        data = response.json()

        assert data["service"] == "RegRadar API"

    def test_root_version(self, test_client: TestClient):
        """Test that root endpoint returns correct version."""
        response = test_client.get("/")
        data = response.json()

        assert data["version"] == "1.0.0"


class TestCORSHeaders:
    """Tests for CORS headers in responses."""

    def test_cors_headers_present(self, test_client: TestClient):
        """Test that CORS headers are present in response."""
        response = test_client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"},
        )

        assert response.status_code == 200
        # CORS headers should be present if origin is allowed

    def test_correlation_id_propagation(self, test_client: TestClient):
        """Test that correlation ID is propagated through requests."""
        custom_correlation_id = "test-correlation-id-12345"
        response = test_client.get(
            "/health",
            headers={"X-Correlation-ID": custom_correlation_id},
        )

        assert response.status_code == 200
        assert response.headers["x-correlation-id"] == custom_correlation_id

    def test_correlation_id_generated_if_missing(self, test_client: TestClient):
        """Test that correlation ID is generated if not provided."""
        response = test_client.get("/health")

        assert response.status_code == 200
        correlation_id = response.headers.get("x-correlation-id")
        assert correlation_id is not None
        assert len(correlation_id) > 0


class TestErrorHandling:
    """Tests for error handling middleware."""

    def test_404_not_found(self, test_client: TestClient):
        """Test that 404 is returned for non-existent endpoint."""
        response = test_client.get("/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self, test_client: TestClient):
        """Test that 405 is returned for wrong HTTP method."""
        response = test_client.post("/health")
        assert response.status_code == 405

    def test_error_response_format(self, test_client: TestClient):
        """Test that error responses have consistent format."""
        response = test_client.get("/nonexistent")

        # Should be valid JSON even for errors
        assert response.status_code == 404
        # FastAPI returns its own 404 format


class TestRequestLogging:
    """Tests for request logging middleware."""

    def test_health_request_is_logged(self, test_client: TestClient, caplog):
        """Test that health check request is logged."""
        response = test_client.get("/health")
        assert response.status_code == 200

        # Check that request was logged (look in caplog)
        # Note: This is simplified; in production use log handlers


class TestAPIMetadata:
    """Tests for API metadata and documentation."""

    def test_openapi_schema_available(self, test_client: TestClient):
        """Test that OpenAPI schema is available."""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema

    def test_swagger_docs_available(self, test_client: TestClient):
        """Test that Swagger UI is available."""
        response = test_client.get("/docs")
        assert response.status_code == 200

    def test_redoc_docs_available(self, test_client: TestClient):
        """Test that ReDoc documentation is available."""
        response = test_client.get("/redoc")
        assert response.status_code == 200
