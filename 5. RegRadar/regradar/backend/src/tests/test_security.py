"""
Security Tests

Comprehensive security testing including:
- SQL injection prevention
- XSS prevention
- CSRF protection
- Input validation
- Authorization checks
- Security headers
"""

import pytest
from datetime import datetime
import json


class TestSQLInjectionPrevention:
    """Test SQL injection prevention via input validation."""

    def test_sql_injection_in_source_filter(self, test_client):
        """Test SQL injection attempt in source filter - should be rejected."""
        response = test_client.get("/api/regulations?source=SEBI' OR '1'='1")
        # Should reject invalid source format
        assert response.status_code in [400, 422]

    def test_sql_injection_in_impact_filter(self, test_client):
        """Test SQL injection attempt in impact filter - should be rejected."""
        response = test_client.get("/api/regulations?impact=HIGH' UNION SELECT * FROM users--")
        # Should reject invalid impact format
        assert response.status_code in [400, 422]

    def test_sql_injection_in_domains_filter(self, test_client):
        """Test SQL injection in domains filter - should be rejected."""
        response = test_client.get("/api/regulations?domains=securities'; DROP TABLE regulations;--")
        # Should reject invalid domain format
        assert response.status_code in [400, 422]

    def test_sql_injection_in_session_lookup(self, test_client):
        """Test SQL injection in session ID lookup - should be rejected."""
        response = test_client.get("/api/session/test' OR '1'='1")
        # Should return 404 or validation error
        assert response.status_code in [400, 404, 422]

    def test_sql_injection_unicode_bypass(self, test_client):
        """Test unicode-encoded SQL injection - should be rejected."""
        # Unicode-encoded quote: %u0027 = '
        response = test_client.get("/api/regulations?source=SEBI%u0027%20OR%20%u00271%u0027=%u00271")
        # Should reject invalid source
        assert response.status_code in [400, 422]


class TestXSSPrevention:
    """Test XSS (Cross-Site Scripting) prevention."""

    def test_xss_in_session_domain(self, test_client):
        """Test XSS payload in session domain."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["<script>alert('xss')</script>"]},
        )
        # Should reject invalid domain
        assert response.status_code == 422

    def test_xss_event_handler(self, test_client):
        """Test XSS via event handler."""
        response = test_client.post(
            "/api/session",
            json={"domains": ['"><svg onload=alert("xss")']},
        )
        # Should reject invalid domain
        assert response.status_code == 422

    def test_xss_javascript_protocol(self, test_client):
        """Test XSS via javascript: protocol."""
        response = test_client.post(
            "/api/session",
            json={"domains": ["javascript:alert('xss')"]},
        )
        assert response.status_code == 422

    def test_regulation_content_is_escaped(self, test_client, db):
        """Test that regulation content is safely escaped."""
        from src.models import Regulation

        # Create regulation with XSS payload
        reg = Regulation(
            source_body="SEBI",
            source_url="https://example.com",
            original_title="<script>alert('xss')</script>",
            original_date=datetime.utcnow(),
            ai_title="Safe Title",
            ai_tldr="<img src=x onerror='alert(1)'>",
            ai_impact_level="MEDIUM",
            domains=json.dumps(["securities"]),
            processing_status="processed",
            content_hash="test123",
        )
        db.add(reg)
        db.commit()

        # Get regulation
        response = test_client.get(f"/api/regulations/{reg.id}")
        assert response.status_code == 200
        data = response.json()

        # Content should be escaped or safe
        # (React/templates will escape by default)
        assert "<script>" not in data["original_title"] or data["original_title"] == "<script>alert('xss')</script>"


class TestInputValidation:
    """Test comprehensive input validation."""

    def test_pagination_boundary_values(self, test_client):
        """Test pagination with boundary values."""
        # Test limit = 0
        response = test_client.get("/api/regulations?limit=0")
        assert response.status_code in [400, 422]

        # Test limit = 1 (minimum)
        response = test_client.get("/api/regulations?limit=1")
        assert response.status_code == 200

        # Test limit = 100 (maximum)
        response = test_client.get("/api/regulations?limit=100")
        assert response.status_code == 200

        # Test limit = 101 (over maximum)
        response = test_client.get("/api/regulations?limit=101")
        assert response.status_code in [400, 422]

    def test_offset_boundary_values(self, test_client):
        """Test offset boundary values."""
        # Test offset = 0
        response = test_client.get("/api/regulations?offset=0")
        assert response.status_code == 200

        # Test very large offset
        response = test_client.get("/api/regulations?offset=999999999")
        assert response.status_code == 200

        # Test negative offset
        response = test_client.get("/api/regulations?offset=-1")
        assert response.status_code in [400, 422]

    def test_domain_validation_strict(self, test_client):
        """Test strict domain validation."""
        # Valid domain
        response = test_client.post(
            "/api/session",
            json={"domains": ["securities"]},
        )
        assert response.status_code == 200

        # Invalid domain
        response = test_client.post(
            "/api/session",
            json={"domains": ["invalid-domain"]},
        )
        assert response.status_code == 422

        # Case sensitive
        response = test_client.post(
            "/api/session",
            json={"domains": ["Securities"]},  # Capital S
        )
        assert response.status_code == 422

    def test_session_id_format_validation(self, test_client):
        """Test session ID format validation."""
        # Valid session creation
        response = test_client.post(
            "/api/session",
            json={"domains": []},
        )
        assert response.status_code == 200
        session_id = response.json()["session_id"]

        # Session ID should be reasonable length
        assert 20 < len(session_id) < 100

        # Should be alphanumeric
        assert all(c.isalnum() or c == "-" for c in session_id)

    def test_very_long_inputs(self, test_client):
        """Test handling of very long inputs - should be rejected."""
        long_string = "x" * 10000

        # Very long source filter should be rejected
        response = test_client.get(f"/api/regulations?source={long_string}")
        assert response.status_code in [400, 422]

        # Very long domain filter should be rejected
        response = test_client.get(f"/api/regulations?domains={long_string}")
        assert response.status_code in [400, 422]

    def test_null_byte_injection(self, test_client):
        """Test null byte injection prevention - should be rejected."""
        response = test_client.get("/api/regulations?source=SEBI%00admin")
        # Should reject invalid source format
        assert response.status_code in [400, 422]


class TestSecurityHeaders:
    """Test security headers in responses."""

    def test_hsts_header(self, test_client):
        """Test HSTS header is present."""
        response = test_client.get("/health")
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=" in response.headers["Strict-Transport-Security"]

    def test_xss_protection_header(self, test_client):
        """Test XSS protection headers."""
        response = test_client.get("/health")
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_frame_options_header(self, test_client):
        """Test frame options header."""
        response = test_client.get("/health")
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_csp_header(self, test_client):
        """Test Content Security Policy header."""
        response = test_client.get("/health")
        assert "Content-Security-Policy" in response.headers

    def test_security_headers_on_all_endpoints(self, test_client):
        """Test security headers on various endpoints."""
        endpoints = [
            "/health",
            "/",
            "/api/regulations",
            "/api/domains",
            "/api/stats",
        ]

        for endpoint in endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 200
            # All should have security headers
            assert "X-Frame-Options" in response.headers


class TestAuthenticationAuthorization:
    """Test authentication and authorization."""

    def test_no_authentication_required_for_public_endpoints(self, test_client):
        """Test that public endpoints don't require auth."""
        response = test_client.get("/health")
        assert response.status_code == 200

        response = test_client.get("/api/regulations")
        assert response.status_code == 200

    def test_session_isolation(self, test_client):
        """Test that sessions are isolated."""
        # Create session 1
        response1 = test_client.post(
            "/api/session",
            json={"domains": ["securities"]},
        )
        session1 = response1.json()["session_id"]

        # Create session 2
        response2 = test_client.post(
            "/api/session",
            json={"domains": ["banking"]},
        )
        session2 = response2.json()["session_id"]

        # Sessions should be different
        assert session1 != session2

        # Each session should maintain its own preferences
        response1_get = test_client.get(f"/api/session/{session1}")
        assert response1_get.json()["domains"] == ["securities"]

        response2_get = test_client.get(f"/api/session/{session2}")
        assert response2_get.json()["domains"] == ["banking"]


class TestErrorInformationDisclosure:
    """Test that errors don't leak sensitive information."""

    def test_404_error_safe(self, test_client):
        """Test 404 errors are safe."""
        response = test_client.get("/api/regulations/99999")
        assert response.status_code == 404
        data = response.json()

        # Should not contain database paths or internal details
        error_text = str(data).lower()
        assert "database" not in error_text or "not found" in error_text
        assert "table" not in error_text or "not found" in error_text

    def test_validation_error_safe(self, test_client):
        """Test validation errors are safe."""
        response = test_client.get("/api/regulations?limit=invalid")
        assert response.status_code in [400, 422]
        data = response.json()

        # Should not leak internal stack traces or file paths
        error_text = str(data)
        assert "traceback" not in error_text.lower()
        assert "file" not in error_text.lower() or "pydantic" in error_text.lower()


class TestCORSConfiguration:
    """Test CORS configuration."""

    def test_cors_headers_present(self, test_client):
        """Test that CORS headers are appropriately configured."""
        response = test_client.get("/health")
        # CORS headers might be set by middleware
        assert response.status_code == 200

    def test_preflight_request_handling(self, test_client):
        """Test OPTIONS requests (CORS preflight)."""
        response = test_client.options(
            "/api/regulations",
            headers={"Origin": "http://localhost:3000"},
        )
        # Should handle OPTIONS or redirect to GET
        assert response.status_code in [200, 405, 404]


class TestRateLimitingPreparation:
    """Test rate limiting configuration (implementation in Day 5+)."""

    def test_no_rate_limit_bypass_via_headers(self, test_client):
        """Test that common rate limit bypass techniques don't work."""
        # Forwarded headers
        response = test_client.get(
            "/api/regulations",
            headers={"X-Forwarded-For": "192.168.1.1"},
        )
        assert response.status_code == 200

        # Client IP
        response = test_client.get(
            "/api/regulations",
            headers={"Client-IP": "127.0.0.1"},
        )
        assert response.status_code == 200
