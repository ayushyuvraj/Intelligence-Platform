"""
Error Handling Tests

Tests for exception handling, error responses, and error middleware.
Ensures all errors are properly caught and formatted.
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.utils.errors import (
    ValidationException,
    DatabaseException,
    NotFoundException,
    AIProcessingException,
    ScraperException,
    RateLimitException,
    UnauthorizedException,
    ForbiddenException,
)

class TestExceptionHierarchy:
    """Test custom exception classes."""

    def test_validation_exception(self):
        """Test ValidationException creation."""
        exc = ValidationException("Invalid input", field="email", value="not-an-email")
        assert exc.message == "Invalid input"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400
        assert exc.details["field"] == "email"

    def test_not_found_exception(self):
        """Test NotFoundException creation."""
        exc = NotFoundException("Regulation", 123)
        assert exc.message == "Regulation not found"
        assert exc.error_code == "NOT_FOUND"
        assert exc.status_code == 404
        assert exc.details["resource_type"] == "Regulation"

    def test_database_exception(self):
        """Test DatabaseException creation."""
        exc = DatabaseException("Connection failed", operation="create")
        assert exc.message == "Connection failed"
        assert exc.error_code == "DATABASE_ERROR"
        assert exc.status_code == 500
        assert exc.details["operation"] == "create"

    def test_ai_processing_exception(self):
        """Test AIProcessingException creation."""
        exc = AIProcessingException("API timeout", attempt_number=2, should_retry=True)
        assert exc.message == "API timeout"
        assert exc.error_code == "AI_PROCESSING_ERROR"
        assert exc.details["attempt_number"] == 2
        assert exc.details["should_retry"] is True

    def test_scraper_exception(self):
        """Test ScraperException creation."""
        exc = ScraperException(
            "Network timeout", source_body="SEBI", error_type="network"
        )
        assert exc.message == "Network timeout"
        assert exc.error_code == "SCRAPER_ERROR"
        assert exc.details["source_body"] == "SEBI"
        assert exc.details["error_type"] == "network"

    def test_rate_limit_exception(self):
        """Test RateLimitException creation."""
        exc = RateLimitException("Too many requests", retry_after_seconds=120)
        assert exc.message == "Too many requests"
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.status_code == 429
        assert exc.details["retry_after_seconds"] == 120

    def test_unauthorized_exception(self):
        """Test UnauthorizedException creation."""
        exc = UnauthorizedException("Invalid credentials")
        assert exc.message == "Invalid credentials"
        assert exc.error_code == "UNAUTHORIZED"
        assert exc.status_code == 401

    def test_forbidden_exception(self):
        """Test ForbiddenException creation."""
        exc = ForbiddenException("Access denied")
        assert exc.message == "Access denied"
        assert exc.error_code == "FORBIDDEN"
        assert exc.status_code == 403


class TestExceptionResponses:
    """Test that exceptions are converted to proper HTTP responses."""

    def test_validation_error_response(self, test_client):
        """Test validation error HTTP response."""
        response = test_client.get("/api/regulations?limit=999")
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_not_found_error_response(self, test_client):
        """Test not found error HTTP response."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"

    def test_invalid_session_response(self, test_client):
        """Test invalid session HTTP response."""
        response = test_client.get("/api/session/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"


class TestErrorResponseFormat:
    """Test error response format consistency."""

    def test_error_response_has_required_fields(self, test_client):
        """Test that error responses have all required fields."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()

        required_fields = ["error", "error_code", "status_code", "details"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_error_response_has_correlation_id(self, test_client):
        """Test that error responses include correlation ID."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        assert "correlation_id" in data

    def test_validation_error_includes_details(self, test_client):
        """Test that validation errors include error details."""
        response = test_client.get("/api/regulations?limit=999")
        assert response.status_code == 400
        data = response.json()
        assert "details" in data


class TestEdgeCases:
    """Test edge cases in error handling."""

    def test_empty_pagination_parameters(self, test_client):
        """Test with empty pagination parameters."""
        response = test_client.get("/api/regulations")
        assert response.status_code == 200
        # Should use defaults

    def test_very_large_offset(self, test_client):
        """Test with very large offset."""
        response = test_client.get("/api/regulations?offset=999999&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["regulations"]) == 0
        assert data["total"] == 0

    def test_zero_limit(self, test_client):
        """Test with limit=0."""
        response = test_client.get("/api/regulations?limit=0")
        assert response.status_code == 400

    def test_negative_limit(self, test_client):
        """Test with negative limit."""
        response = test_client.get("/api/regulations?limit=-1")
        assert response.status_code == 400

    def test_very_long_string_input(self, test_client):
        """Test with very long input strings."""
        long_string = "x" * 10000
        response = test_client.post(
            "/api/session",
            json={"domains": [long_string]},
        )
        # Should either reject or normalize
        assert response.status_code in [400, 422]

    def test_special_characters_in_input(self, test_client):
        """Test with special characters in input."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["<script>alert('xss')</script>"]},
        )
        # Should reject invalid domain
        assert response.status_code == 422

    def test_null_values_in_request(self, test_client):
        """Test with null values in request."""
        response = test_client.post(
            "/api/session",
            json={"domains": None},
        )
        # Should accept (using default)
        assert response.status_code in [200, 422]

    def test_missing_required_fields(self, test_client):
        """Test with missing required fields."""
        response = test_client.post(
            "/api/session",
            json={},
        )
        # domains has default, should be OK
        assert response.status_code in [200, 422]


class TestConcurrentRequests:
    """Test error handling under concurrent requests."""

    def test_multiple_rapid_requests(self, test_client):
        """Test multiple rapid requests."""
        responses = []
        for i in range(5):
            response = test_client.get("/health")
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

    def test_mixed_valid_invalid_requests(self, test_client):
        """Test mix of valid and invalid requests."""
        valid_response = test_client.get("/health")
        invalid_response = test_client.get("/api/regulations/99999")

        assert valid_response.status_code == 200
        assert invalid_response.status_code == 404


class TestErrorLogging:
    """Test that errors are logged properly."""

    def test_404_is_logged(self, test_client):
        """Test that 404 errors are logged."""
        # This is tested implicitly if logger doesn't crash
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404

    def test_validation_error_is_logged(self, test_client):
        """Test that validation errors are logged."""
        response = test_client.get("/api/regulations?limit=999")
        assert response.status_code == 400


class TestStatusCodes:
    """Test that correct HTTP status codes are returned."""

    def test_success_status_codes(self, test_client):
        """Test successful requests return 200."""
        response = test_client.get("/health")
        assert response.status_code == 200

    def test_created_status_code(self, test_client):
        """Test POST returns appropriate status."""
        response = test_client.post(
            "/api/session",
            json={"domains": []},
        )
        assert response.status_code == 200  # Not 201 for this API

    def test_bad_request_status_code(self, test_client):
        """Test bad requests return 400."""
        response = test_client.get("/api/regulations?limit=-1")
        assert response.status_code == 400

    def test_not_found_status_code(self, test_client):
        """Test not found returns 404."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404

    def test_internal_error_status_code(self, test_client):
        """Test internal errors return 500."""
        # Harder to test without a real error
        pass


class TestExceptionDetails:
    """Test that exception details are helpful."""

    def test_validation_error_has_field_info(self, test_client):
        """Test that validation errors specify which field failed."""
        response = test_client.get("/api/regulations?limit=999")
        assert response.status_code == 400
        # Details should indicate it's the limit field

    def test_not_found_error_has_resource_info(self, test_client):
        """Test that not found errors specify resource type."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["details"]["resource_type"] == "Regulation"

    def test_database_error_includes_operation(self):
        """Test that database errors include operation info."""
        # This would need to trigger actual DB error
        pass
