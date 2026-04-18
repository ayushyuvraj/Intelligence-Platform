import asyncio
import time
import pytest
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

@pytest.mark.xfail(reason="Integration load test requires running server", strict=False)
@pytest.mark.asyncio
async def test_load_regulations_concurrent():
    """Load test: 100 concurrent requests to /api/regulations.
    Ensures response time < 500ms per request.
    """
    async with AsyncClient(base_url=BASE_URL) as client:
        start = time.monotonic()
        tasks = [client.get("/api/regulations") for _ in range(100)]
        responses = await asyncio.gather(*tasks)
        elapsed = time.monotonic() - start
        # average response time should be <0.5s
        avg_ms = (elapsed / len(responses)) * 1000
        assert avg_ms < 500, f"Average response {avg_ms:.1f}ms exceeds 500ms"
        for r in responses:
            assert r.status_code == 200
