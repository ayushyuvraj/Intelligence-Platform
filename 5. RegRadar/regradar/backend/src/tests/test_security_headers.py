import pytest
from httpx import Client

BASE_URL = "http://localhost:8000"

@pytest.mark.xfail(reason="Security header test requires running server", strict=False)
def test_security_headers():
    with Client(base_url=BASE_URL) as client:
        r = client.get("/health")
        assert r.status_code == 200
        headers = r.headers
        # Security headers per CLAUDE.md
        assert headers.get("Strict-Transport-Security") is not None, "Missing HSTS"
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert headers.get("X-XSS-Protection") == "1; mode=block"
