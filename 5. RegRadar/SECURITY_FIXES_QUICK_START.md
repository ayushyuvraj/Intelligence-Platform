# RegRadar Security Fixes - Quick Start Guide

**For:** Development Team  
**Updated:** April 18, 2026  
**Time to Complete:** 8-10 hours (full fixes), 2-3 hours (critical path)

---

## TL;DR - The 15 Vulnerabilities

| # | Issue | Severity | Impact | Fix Time |
|---|-------|----------|--------|----------|
| 1 | React doubled HTML tags | CRITICAL | Frontend won't compile | 0.75h |
| 2 | Hardcoded API key | CRITICAL | Secret exposure | 1.5h |
| 3 | No scraper auth | CRITICAL | Unauthenticated access | 0.75h |
| 4 | SQL injection in filter | CRITICAL | Database breach | 1.75h |
| 5 | Race condition AI | CRITICAL | Data corruption | 2.5h |
| 6 | No API timeout | CRITICAL | Thread starvation | 1.5h |
| 7 | N+1 query stats | CRITICAL | DoS/memory crash | 2.5h |
| 8 | console.log | HIGH | Info leak | 1.5h |
| 9 | No rate limiting | HIGH | DoS attacks | 2.25h |
| 10 | Incomplete error handling | HIGH | Scraper crashes | 1.5h |
| 11 | No pagination validation | HIGH | OOM attacks | 0.75h |
| 12 | Unencrypted backups | HIGH | Data compromise | 1h |
| 13 | No request timeout | HIGH | Thread starvation | 0.5h |
| 14 | CORS not validated | HIGH | XSS/CSRF | 0.5h |
| 15 | Insufficient logging | HIGH | Forensics gap | 1.5h |

---

## Phase 1: GET FRONTEND COMPILING (30 minutes)

### What's Wrong
`FeedPage.tsx` has 16+ doubled HTML tags: `<<divdiv>>`, `<<headerheader>>`, `<<inputinput>>`, etc.

### How to Fix
**File:** `regradar/frontend/src/pages/FeedPage.tsx`

Search and replace (16 occurrences):
```
<<divdiv          → <div
<<headerheader    → <header
<<hh1             → <h1
<<pp              → <p
<<SearchSearch    → <Search
<<inputinput      → <input
<<buttonbutton    → <button
<<FilterFilter    → <Filter
<<LoaderLoader2   → <Loader2
<<RegulationRegulationCard → <RegulationCard
```

Also fix TypeScript types:
- Line 9: `useState<<anyany[]>([])` → `useState<any[]>([])`
- Line 12: `useState<<stringstring[]>([])` → `useState<string[]>([])`

### Verify It Works
```bash
cd regradar/frontend
npm run build
# Should complete without errors
```

✅ **Frontend builds. You can now see the UI.**

---

## Phase 2: SECURE THE API (1-2 hours)

### What's Wrong
1. **Dev API key is hardcoded** - visible in code
2. **Scraper endpoint has no auth** - anyone can call it
3. **Domain filter uses string interpolation** - SQL injection vulnerability

### How to Fix (in order)

#### Step 1: Remove Hardcoded API Key
**File:** `regradar/backend/src/config.py:55`

Before:
```python
api_key_scraper: str = "dev_key_change_in_prod"
```

After:
```python
api_key_scraper: str = Field(..., description="Scraper API key from environment")
```

Add import at top:
```python
from pydantic import Field
```

Create `.env.example`:
```
API_KEY_SCRAPER=your_scraper_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

Copy to `.env` and add real keys (don't commit `.env`).

#### Step 2: Require API Key on Scraper Endpoint
**File:** `regradar/backend/src/api/dependencies.py:43-63`

Replace `verify_api_key()` function:
```python
from src.config import settings

async def verify_api_key(
    x_api_key: str = Header(None),
) -> str:
    """Verify API key for scraper requests."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header required",
        )
    
    if x_api_key != settings.api_key_scraper:
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
    
    return x_api_key
```

**File:** `regradar/backend/src/api/routes.py:519`

Add dependency to `get_scraper_runs`:
```python
@router.get("/scraper-runs", tags=["Scraper"])
async def get_scraper_runs(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    source: str = Query("", description="Filter by source body"),
    api_key: str = Depends(verify_api_key),  # ← ADD THIS
    db: Session = Depends(get_db),
) -> dict:
```

#### Step 3: Fix SQL Injection in Domain Filter
**File:** `regradar/backend/src/api/routes.py:84-88`

Add whitelist at top of file:
```python
VALID_DOMAINS = {
    "banking", "securities", "insurance", "capital_markets",
    "derivatives", "commodities", "pension", "microfinance",
    "payment_systems"
}

def validate_domain(domain: str) -> bool:
    """Validate domain against whitelist."""
    return domain.strip().lower() in VALID_DOMAINS
```

Replace the domain filter:
```python
if domains:
    domain_list = [d.strip().lower() for d in domains.split(",") if d.strip()]
    
    # Validate all domains
    for domain in domain_list:
        if not validate_domain(domain):
            raise ValidationException(
                f"Invalid domain: {domain}",
                "domains",
                domain
            )
    
    # Safe query using parameterized contains
    for domain in domain_list:
        query = query.filter(
            Regulation.domains.astext.contains(f'"{domain}"')
        )
```

### Verify It Works
```bash
cd regradar/backend

# Test 1: No auth header
curl http://localhost:8000/api/scraper-runs
# Should return 401: "X-API-Key header required"

# Test 2: Invalid key
curl -H "X-API-Key: wrong" http://localhost:8000/api/scraper-runs
# Should return 403: "Invalid API key"

# Test 3: Valid key
curl -H "X-API-Key: $API_KEY_SCRAPER" http://localhost:8000/api/scraper-runs
# Should return 200 with scraper runs

# Test 4: SQL injection blocked
curl "http://localhost:8000/api/regulations?domains=banking%22;DROP%20TABLE--"
# Should return 400: "Invalid domain"

# Test 5: Valid domain works
curl "http://localhost:8000/api/regulations?domains=banking"
# Should return 200 with regulations
```

✅ **API is secure. Authentication and input validation working.**

---

## Phase 3: PREVENT CRASHES (2 hours)

### What's Wrong
1. **AI processing can hang forever** - no timeout
2. **Stats endpoint loads all records** - OutOfMemory on 10k+ regulations
3. **Concurrent AI updates collide** - data corruption possible

### How to Fix (in order)

#### Step 1: Add Timeout to AI Engine
**File:** `regradar/backend/src/ai/engine.py:37-50`

Import asyncio at top:
```python
import asyncio
```

Replace `_call_gemini()` method:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((TimeoutError, asyncio.TimeoutError)),
)
async def _call_gemini(self, prompt: str) -> str:
    """Call Gemini API with strict timeout enforcement."""
    async with self._semaphore:
        loop = asyncio.get_event_loop()
        
        try:
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(
                        prompt,
                        generation_config={"response_mime_type": "application/json"}
                    )
                ),
                timeout=settings.gemini_timeout_seconds
            )
            return response.text
            
        except asyncio.TimeoutError as e:
            logger.error(
                "Gemini API call timed out",
                extra={
                    "timeout_seconds": settings.gemini_timeout_seconds,
                    "prompt_length": len(prompt),
                }
            )
            raise TimeoutError(f"Gemini API timeout after {settings.gemini_timeout_seconds}s") from e
```

#### Step 2: Fix N+1 Query in Stats
**File:** `regradar/backend/src/api/routes.py:298-351`

Replace the whole `get_stats()` function with batch processing:
```python
@router.get("/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    """Get statistics dashboard data with optimized queries."""
    import time
    start_time = time.time()
    
    try:
        # Fast aggregate queries
        total = db.query(func.count(Regulation.id)).scalar() or 0
        
        # By source body
        by_source = {}
        for source, count in db.query(
            Regulation.source_body, func.count(Regulation.id)
        ).group_by(Regulation.source_body).all():
            by_source[source] = count
        
        # By impact level
        by_impact = {}
        for impact, count in db.query(
            Regulation.ai_impact_level, func.count(Regulation.id)
        ).group_by(Regulation.ai_impact_level).all():
            by_impact[impact] = count
        
        # By domain - STREAMING (not all at once)
        by_domain = {}
        BATCH_SIZE = 1000
        
        for offset in range(0, total, BATCH_SIZE):
            regulations_batch = db.query(Regulation.id, Regulation.domains)\
                .offset(offset)\
                .limit(BATCH_SIZE)\
                .all()
            
            for reg_id, domains_json in regulations_batch:
                try:
                    domains = json.loads(domains_json)
                    for domain in domains:
                        by_domain[domain] = by_domain.get(domain, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Time series
        time_series = RegulationService.get_time_series_stats(db)
        
        # Last update
        last_regulation = db.query(Regulation).order_by(desc(Regulation.created_at)).first()
        last_updated = last_regulation.created_at if last_regulation else datetime.utcnow()
        
        query_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Stats retrieved",
            extra={
                "total_regulations": total,
                "query_time_ms": query_time_ms,
            }
        )
        
        return {
            "total_regulations": total,
            "by_source": by_source,
            "by_impact": by_impact,
            "by_domain": by_domain,
            "last_updated": last_updated,
            "trends": time_series
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise DatabaseException(str(e), "get_stats")
```

#### Step 3: Prevent Race Conditions
**File:** `regradar/backend/src/scraper/runner.py:30-84`

Replace `run_ai_processing()` with pessimistic locking:
```python
async def run_ai_processing():
    """Process pending regulations with row-level locking."""
    job_start_time = datetime.utcnow()
    start_ms = time.time()

    logger.info("Starting AI processing job")

    try:
        db = next(get_db())
        engine = GeminiEngine()

        # Lock rows to prevent race conditions
        pending_regs = db.query(Regulation)\
            .filter(Regulation.processing_status == "pending")\
            .with_for_update(skip_locked=True)\
            .all()

        if not pending_regs:
            logger.info("No pending regulations to process")
            return

        processed_count = 0
        failed_count = 0

        for reg in pending_regs:
            try:
                # Re-check status after lock
                if reg.processing_status != "pending":
                    continue

                # Analyze
                analysis = await engine.analyze_regulation(reg.full_text)

                # Update fields
                reg.ai_title = analysis.ai_title
                reg.ai_tldr = analysis.ai_tldr
                reg.ai_what_changed = analysis.ai_what_changed
                reg.ai_who_affected = ", ".join(analysis.ai_who_affected)
                reg.ai_action_required = "\n".join(analysis.ai_action_required)
                reg.ai_impact_level = analysis.ai_impact_level
                reg.domains = json.dumps(analysis.domains)
                reg.processing_status = "completed"

                # Atomic commit
                db.commit()
                processed_count += 1

            except TimeoutError as e:
                db.rollback()
                logger.error(f"Timeout for reg {reg.id}")
                reg.processing_status = "review_pending"
                reg.ai_title = "TIMEOUT: Manual review required"
                db.commit()
                failed_count += 1
                
            except Exception as e:
                db.rollback()
                logger.error(f"AI analysis failed for reg {reg.id}: {str(e)}")
                reg.processing_status = "review_pending"
                db.commit()
                failed_count += 1

        duration_ms = int((time.time() - start_ms) * 1000)
        logger.info(
            "AI processing completed",
            extra={
                "processed": processed_count,
                "failed": failed_count,
                "duration_ms": duration_ms
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error in AI processing: {str(e)}")
    finally:
        try:
            if 'db' in locals():
                db.close()
        except Exception as e:
            logger.error(f"Error closing DB: {str(e)}")
```

### Verify It Works
```bash
cd regradar/backend

# Test 1: API timeout
# (Manually test with slow response)

# Test 2: Stats endpoint
curl http://localhost:8000/api/stats
# Should return <500ms response, even with 10k regulations

# Test 3: Concurrent processing
# (Should not corrupt data)
pytest tests/test_concurrency.py -v
```

✅ **API is reliable. No hangs, no memory crashes, no race conditions.**

---

## Phase 4: SECURE & MONITOR (1-2 hours)

### What's Wrong
1. **Console.log exposes data** - remove from production
2. **No rate limiting** - DoS attacks possible
3. **Insufficient logging** - can't debug security issues

### How to Fix (Quick Version)

#### Step 1: Remove Console.log
**File:** `regradar/frontend/src/pages/FeedPage.tsx:26, 43`

Replace:
```javascript
} catch (e) {
    console.error("Init error", e);
}
```

With:
```javascript
import { logger } from '../utils/logger';

} catch (e) {
    logger.error("Failed to initialize feed", {
        error: e instanceof Error ? e.message : String(e),
    });
}
```

Create `regradar/frontend/src/utils/logger.ts`:
```typescript
export class FrontendLogger {
  isDevelopment: boolean;

  constructor() {
    this.isDevelopment = import.meta.env.DEV;
  }

  error(message: string, context?: Record<string, any>): void {
    if (this.isDevelopment) {
      console.error(message, context);
    } else {
      // In production, send to backend via /api/logs
      fetch("/api/logs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ level: "error", message, context }),
      }).catch(() => {});
    }
  }
}

export const logger = new FrontendLogger();
```

#### Step 2: Add Rate Limiting
**File:** `regradar/backend/requirements.txt`

Add:
```
slowapi>=0.1.9
```

**File:** `regradar/backend/src/main.py`

Add after app creation:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Too many requests", "error_code": "RATE_LIMITED"},
    )
```

**File:** `regradar/backend/src/api/routes.py`

Add import:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

Add to endpoints:
```python
@limiter.limit("30/minute")
@router.get("/regulations", response_model=RegulationListResponse)
async def list_regulations(...):
    # ...

@limiter.limit("20/minute")
@router.get("/my-feed", response_model=RegulationListResponse)
async def get_my_feed(...):
    # ...

@limiter.limit("10/minute")
@router.get("/stats", response_model=StatsResponse)
async def get_stats(...):
    # ...
```

#### Step 3: Add Security Logging
**File:** `regradar/backend/src/api/dependencies.py`

Add logging to `verify_api_key()`:
```python
logger.warning(
    "Invalid API key attempt",
    extra={
        "endpoint": "scraper-runs",
        "key_length": len(x_api_key) if x_api_key else 0,
    }
)
```

### Verify It Works
```bash
cd regradar/frontend
npm run lint  # Should show no console.* errors

cd regradar/backend
pip install slowapi

# Test rate limiting
for i in {1..35}; do
    curl http://localhost:8000/api/regulations -H "X-API-Key: test"
done
# Last 5 should return 429
```

✅ **Code quality improved. Rate limiting active. Security logging in place.**

---

## Timeline

| Phase | Time | Priority |
|-------|------|----------|
| **Phase 1: Compilation** | 0.75h | 🔴 CRITICAL |
| **Phase 2: Security** | 3.5h | 🔴 CRITICAL |
| **Phase 3: Reliability** | 4.5h | 🔴 CRITICAL |
| **Phase 4: Quality** | 2.5h | 🟡 HIGH |
| **Total** | **11.25h** | |

**Critical Path Only (P1-P3):** 8.75 hours → Ready for production

---

## Testing Everything

### Backend Tests
```bash
cd regradar/backend
pytest -v --cov=src --cov-report=term-missing
# Should see 80%+ coverage
```

### Frontend Build
```bash
cd regradar/frontend
npm run build
# Should complete without errors
```

### Smoke Tests
```bash
# API starts
curl http://localhost:8000/health

# Frontend loads
curl http://localhost:3000

# Authentication works
curl -H "X-API-Key: $API_KEY_SCRAPER" http://localhost:8000/api/scraper-runs

# Rate limiting works
curl http://localhost:8000/api/regulations
# Make 31 requests, last one returns 429
```

---

## Deployment

1. **Test locally first** - run all tests
2. **Create backup** - save current database
3. **Deploy backend** - stop, update code, start
4. **Deploy frontend** - rebuild and redeploy
5. **Monitor logs** - watch for errors
6. **Verify endpoints** - test key flows

---

## Need Help?

**Full Details:** See `SECURITY_REMEDIATION_PLAN.md` (80+ step-by-step instructions)  
**Checklist:** See `SECURITY_FIX_CHECKLIST.md` (checkbox tracking)  
**Questions:** Check CLAUDE.md section 7-9 (error handling, logging, security standards)

---

**Status:** Ready to implement  
**Estimated Completion:** 1 sprint (2-3 days with 2-person team)  
**Next Step:** Start Phase 1 (fix React doubled tags) → Verify build succeeds → Proceed to Phase 2

🚀 **Let's secure this product!**
