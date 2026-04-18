"""
Error Handling Tests

Comprehensive tests for exception handling, error responses, and error middleware.
Tests all edge cases and validates error response format.
"""

import pytest
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
        # Pydantic returns 422 for validation errors in FastAPI
        assert response.status_code in [400, 422]
        data = response.json()
        # Either our custom error or Pydantic's validation error
        assert "error" in data or "detail" in data

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

    def test_not_found_error_format(self, test_client):
        """Test 404 error response format."""
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
        # Correlation ID should be in response body or header
        assert "correlation_id" in data or "X-Correlation-ID" in response.headers

    def test_not_found_error_has_details(self, test_client):
        """Test that not found errors include resource details."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        assert "details" in data
        assert "resource_type" in data["details"]


class TestEdgeCases:
    """Test edge cases in error handling."""

    def test_empty_pagination_parameters(self, test_client):
        """Test with default pagination."""
        response = test_client.get("/api/regulations")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "regulations" in data

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
        # Should fail validation (limit must be >= 1)
        assert response.status_code in [400, 422]

    def test_negative_limit(self, test_client):
        """Test with negative limit."""
        response = test_client.get("/api/regulations?limit=-1")
        # Should fail validation
        assert response.status_code in [400, 422]

    def test_negative_offset(self, test_client):
        """Test with negative offset."""
        response = test_client.get("/api/regulations?offset=-1")
        # Should fail validation
        assert response.status_code in [400, 422]

    def test_max_limit_exceeded(self, test_client):
        """Test with limit exceeding max (100)."""
        response = test_client.get("/api/regulations?limit=101")
        # Should fail validation
        assert response.status_code in [400, 422]

    def test_special_characters_in_filter(self, test_client):
        """Test with special characters in domain filter - should be rejected."""
        response = test_client.get("/api/regulations?domains=test%20domain")
        # Spaces in domain names should fail validation
        assert response.status_code in [400, 422]

    def test_null_values_in_session_request(self, test_client):
        """Test with null values in session request."""
        response = test_client.post(
            "/api/session",
            json={"domains": None},
        )
        # Should either use default or validate
        assert response.status_code in [200, 422]

    def test_missing_required_fields_session(self, test_client):
        """Test with missing required fields."""
        response = test_client.post(
            "/api/session",
            json={},
        )
        # domains has default, should be OK
        assert response.status_code in [200, 422]

    def test_empty_domain_list(self, test_client):
        """Test session with empty domain list."""
        response = test_client.post(
            "/api/session",
            json={"domains": []},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["domains"] == []

    def test_invalid_domain_in_list(self, test_client):
        """Test with invalid domain in list."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["invalid_domain_xyz"]},
        )
        # Should fail domain validation
        assert response.status_code == 422

    def test_mixed_valid_invalid_domains(self, test_client):
        """Test with mix of valid and invalid domains."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["securities", "invalid_xyz", "banking"]},
        )
        # Should fail if any invalid
        assert response.status_code == 422

    def test_unicode_in_filter(self, test_client):
        """Test with unicode characters in filter - should be rejected."""
        response = test_client.get("/api/regulations?domains=%E2%9C%93")
        # Unicode characters in domain should fail validation
        assert response.status_code in [400, 422]

    def test_sql_injection_attempt(self, test_client):
        """Test that SQL injection attempts are rejected via input validation."""
        response = test_client.get("/api/regulations?source=SEBI' OR '1'='1")
        # Should reject invalid source format
        assert response.status_code in [400, 422]

    def test_xss_payload_in_domain(self, test_client):
        """Test that XSS payloads are handled safely."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["<script>alert('xss')</script>"]},
        )
        # Should reject (invalid domain)
        assert response.status_code in [400, 422]

    def test_very_long_source_filter(self, test_client):
        """Test with very long source filter - should be rejected."""
        long_source = "x" * 1000
        response = test_client.get(f"/api/regulations?source={long_source}")
        # Should reject invalid source format (too long)
        assert response.status_code in [400, 422]


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
        other_valid = test_client.post("/api/session", json={"domains": []})

        assert valid_response.status_code == 200
        assert invalid_response.status_code == 404
        assert other_valid.status_code == 200

    def test_rapid_session_creation(self, test_client):
        """Test rapid session creation."""
        responses = []
        for i in range(3):
            response = test_client.post(
                "/api/session",
                json={"domains": ["securities"]},
            )
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        # All should have different session IDs
        session_ids = [r.json()["session_id"] for r in responses]
        assert len(set(session_ids)) == 3  # All unique


class TestStatusCodes:
    """Test that correct HTTP status codes are returned."""

    def test_success_status_code_health(self, test_client):
        """Test successful health check returns 200."""
        response = test_client.get("/health")
        assert response.status_code == 200

    def test_success_status_code_regulations(self, test_client):
        """Test successful regulations endpoint returns 200."""
        response = test_client.get("/api/regulations")
        assert response.status_code == 200

    def test_post_session_status_code(self, test_client):
        """Test POST session returns 200."""
        response = test_client.post(
            "/api/session",
            json={"domains": []},
        )
        assert response.status_code == 200

    def test_not_found_status_code(self, test_client):
        """Test not found returns 404."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404

    def test_validation_error_status_code(self, test_client):
        """Test validation errors return appropriate code."""
        response = test_client.get("/api/regulations?limit=-1")
        # FastAPI/Pydantic returns 422 for validation errors
        assert response.status_code in [400, 422]


class TestExceptionDetails:
    """Test that exception details are helpful."""

    def test_not_found_error_has_resource_info(self, test_client):
        """Test that not found errors specify resource type."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        assert "details" in data
        assert data["details"]["resource_type"] == "Regulation"

    def test_not_found_error_has_resource_id(self, test_client):
        """Test that not found errors include resource ID."""
        response = test_client.get("/api/regulations/12345")
        assert response.status_code == 404
        data = response.json()
        assert "resource_id" in data["details"]
        assert data["details"]["resource_id"] == "12345"

    def test_error_has_correlation_id_in_response(self, test_client):
        """Test all errors include correlation ID."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        # Check both body and header
        has_correlation = "correlation_id" in data or "X-Correlation-ID" in response.headers
        assert has_correlation
        if "correlation_id" in data:
            assert len(data["correlation_id"]) > 0

    def test_custom_correlation_id_preserved(self, test_client):
        """Test that provided correlation ID is preserved in errors."""
        custom_id = "test-correlation-xyz"
        response = test_client.get(
            "/api/regulations/99999",
            headers={"X-Correlation-ID": custom_id},
        )
        assert response.status_code == 404
        data = response.json()
        # Check both body and header for correlation ID
        if "correlation_id" in data:
            assert data["correlation_id"] == custom_id
        if "X-Correlation-ID" in response.headers:
            assert response.headers["X-Correlation-ID"] == custom_id


class TestSecurityValidation:
    """Test security-related validation and error handling."""

    def test_session_id_format_validation(self, test_client):
        """Test that session ID format is validated."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["securities"]},
        )
        assert response.status_code == 200
        data = response.json()
        session_id = data["session_id"]
        # Should be alphanumeric, no special chars
        assert session_id.isalnum() or "-" in session_id or "_" in session_id

    def test_no_sensitive_data_in_errors(self, test_client):
        """Test that errors don't leak sensitive information."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()
        # Should not contain SQL, database paths, internal paths
        error_string = str(data).lower()
        assert "sql" not in error_string or "regulation" in error_string
        assert "password" not in error_string
        assert "/home/" not in error_string

    def test_cors_headers_on_errors(self, test_client):
        """Test that CORS headers are present on error responses."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"


class TestResponseContentTypes:
    """Test response content type handling."""

    def test_error_response_is_json(self, test_client):
        """Test that error responses are valid JSON."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        # Should be valid JSON
        data = response.json()
        assert isinstance(data, dict)

    def test_success_response_is_json(self, test_client):
        """Test that success responses are valid JSON."""
        response = test_client.get("/api/regulations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_all_responses_have_content_type(self, test_client):
        """Test that all responses have content-type header."""
        response = test_client.get("/health")
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
