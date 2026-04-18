# RegRadar Security Remediation - Implementation Checklist

**Start Date:** April 18, 2026  
**Target Completion:** April 20, 2026  
**Status:** NOT STARTED

---

## PHASE 1: CRITICAL COMPILATION FIX (0.75 hours)

### Fix #1: React Frontend Won't Compile

**Files to Modify:**
- [ ] `regradar/frontend/src/pages/FeedPage.tsx`

**Steps:**
- [ ] Step 1.1 - Fix doubled div at line 50: `<<divdiv` → `<div`
- [ ] Step 1.2 - Fix doubled header at line 51: `<<headerheader` → `<header`
- [ ] Step 1.3 - Fix doubled h1 at line 53: `<<hh1` → `<h1`
- [ ] Step 1.4 - Fix doubled p at line 54: `<<pp` → `<p`
- [ ] Step 1.5 - Fix doubled div at line 57: `<<divdiv` → `<div`
- [ ] Step 1.6 - Fix doubled div at line 58: `<<divdiv` → `<div`
- [ ] Step 1.7 - Fix doubled Search at line 59: `<<SearchSearch` → `<Search`
- [ ] Step 1.8 - Fix doubled input at line 60: `<<inputinput` → `<input`
- [ ] Step 1.9 - Fix doubled button at line 68: `<<buttonbutton` → `<button`
- [ ] Step 1.10 - Fix doubled Filter at line 72: `<<FilterFilter` → `<Filter`
- [ ] Step 1.11 - Fix doubled div at line 78: `<<divdiv` → `<div`
- [ ] Step 1.12 - Fix doubled Loader2 at line 79: `<<LoaderLoader2` → `<Loader2`
- [ ] Step 1.13 - Fix doubled p at line 80: `<<pp` → `<p`
- [ ] Step 1.14 - Fix doubled div at line 83: `<<divdiv` → `<div`
- [ ] Step 1.15 - Fix doubled RegulationCard at line 86: `<<RegulationRegulationCard` → `<RegulationCard`
- [ ] Step 1.16 - Fix doubled div at line 89: `<<divdiv` → `<div`
- [ ] Step 1.18 - Fix TypeScript types at lines 9, 12: `<<anyany[]>` → `<any[]>` and `<<stringstring[]>` → `<string[]>`

**Verification:**
- [ ] `npm run build` completes without errors
- [ ] `npm run type-check` passes
- [ ] No TypeScript compilation errors
- [ ] ESLint shows no syntax errors

**Test:**
```bash
npm run build
npm run type-check
```

**Commit:**
- [ ] Commit: `[SECURITY] Fix React syntax errors - doubled HTML tags (16 fixes)`

---

## PHASE 2: SECURITY HARDENING (4 hours)

### Fix #2: Hardcoded API Key Exposed

**Files to Modify:**
- [ ] `regradar/backend/src/config.py`
- [ ] `regradar/backend/src/api/dependencies.py`
- [ ] `regradar/backend/src/api/routes.py`
- [ ] Create: `.env.example`
- [ ] Create: `SECURITY_CONFIG.md`

**Steps:**
- [ ] Step 2.1 - Create `.env.example` with placeholders
- [ ] Step 2.2 - Update `config.py:55` to use `Field(...)` instead of default
- [ ] Step 2.3 - Add validation method to reject dev keys in production
- [ ] Step 2.4 - Add Pydantic root_validator for secrets validation
- [ ] Step 2.5 - Update `verify_api_key()` to enforce validation
- [ ] Step 2.6 - Apply API key to scraper endpoint (line 519)
- [ ] Step 2.7 - Verify `.gitignore` excludes `.env`
- [ ] Step 2.8 - Create `SECURITY_CONFIG.md` documentation

**Verification:**
- [ ] `.env.example` created with placeholders
- [ ] `config.py` requires environment variables
- [ ] Validation rejects dev keys in production
- [ ] API key required on `/api/scraper-runs`
- [ ] `.gitignore` prevents `.env` from being committed
- [ ] No hardcoded keys in git history

**Test:**
```bash
# Test without .env
export GEMINI_API_KEY=""
python -c "from src.config import settings" # Should fail

# Test with valid .env
cp .env.example .env
# Add real keys...
python -c "from src.config import settings; print('OK')" # Should pass

# Test API auth
curl -X GET http://localhost:8000/api/scraper-runs  # Should return 401
curl -X GET http://localhost:8000/api/scraper-runs -H "X-API-Key: invalid"  # Should return 403
curl -X GET http://localhost:8000/api/scraper-runs -H "X-API-Key: $(echo $API_KEY_SCRAPER)"  # Should return 200
```

**Commit:**
- [ ] Commit: `[SECURITY] Remove hardcoded API key - use environment variables`

---

### Fix #3: Missing API Authentication on Scraper Endpoints

**Files to Modify:**
- [ ] `regradar/backend/src/api/dependencies.py`
- [ ] `regradar/backend/src/api/routes.py`
- [ ] `regradar/backend/src/tests/test_security.py`

**Steps:**
- [ ] Step 3.1 - (Covered in Fix #2, Step 2.5-2.6)
- [ ] Step 3.2 - Add unit tests for scraper endpoint auth
- [ ] Step 3.3 - Add security logging to verify_api_key

**Verification:**
- [ ] `verify_api_key()` enforces validation
- [ ] `/api/scraper-runs` requires X-API-Key header
- [ ] Invalid keys return 403
- [ ] Valid keys grant access
- [ ] 3 security tests pass

**Test:**
```bash
pytest tests/test_security.py::test_scraper_runs*
```

**Commit:**
- [ ] Commit: `[SECURITY] Add authentication to scraper endpoints`

---

### Fix #4: SQL Injection in Domain Filter

**Files to Modify:**
- [ ] `regradar/backend/src/api/routes.py`
- [ ] `regradar/backend/src/services/regulation_service.py`
- [ ] `regradar/backend/src/api/schemas.py`
- [ ] `regradar/backend/src/tests/test_security.py`

**Steps:**
- [ ] Step 4.1 - Create VALID_DOMAINS whitelist and validate_domain()
- [ ] Step 4.2 - Update list_regulations to validate domains
- [ ] Step 4.3 - Update RegulationService to validate domains
- [ ] Step 4.4 - Add unit tests for SQL injection protection
- [ ] Step 4.5 - Add validation to OpenAPI schemas

**Verification:**
- [ ] VALID_DOMAINS whitelist created
- [ ] `validate_domain()` function works
- [ ] All endpoints validate domains
- [ ] 3 SQL injection tests pass
- [ ] No SQL injection possible

**Test:**
```bash
# Test invalid domain
curl "http://localhost:8000/api/regulations?domains=banking%22%20OR%20%221%22=%221"

# Test valid domain
curl "http://localhost:8000/api/regulations?domains=banking"

pytest tests/test_security.py::test_list_regulations*
```

**Commit:**
- [ ] Commit: `[SECURITY] Prevent SQL injection in domain filter`

---

### Fix #14: Missing CORS Origin Validation

**Files to Modify:**
- [ ] `regradar/backend/src/config.py`
- [ ] `regradar/backend/src/main.py`

**Steps:**
- [ ] Verify CORS origins are explicit (not "*")
- [ ] Add validation that only whitelisted origins are allowed
- [ ] Test CORS with invalid origin

**Verification:**
- [ ] `settings.get_cors_origins()` returns list of specific hosts
- [ ] CORS middleware only allows whitelisted origins
- [ ] Invalid origin returns CORS error

**Test:**
```bash
curl -H "Origin: http://attacker.com" http://localhost:8000/api/regulations -v
# Should NOT have Access-Control-Allow-Origin header

curl -H "Origin: http://localhost:3000" http://localhost:8000/api/regulations -v
# Should have Access-Control-Allow-Origin: http://localhost:3000
```

**Commit:**
- [ ] Commit: `[SECURITY] Enforce CORS origin whitelist`

---

## PHASE 3: RELIABILITY & AVAILABILITY (4.5 hours)

### Fix #5: Race Condition in AI Processing

**Files to Modify:**
- [ ] `regradar/backend/src/models.py`
- [ ] `regradar/backend/src/scraper/runner.py`
- [ ] `regradar/backend/src/api/routes.py`
- [ ] `regradar/backend/src/api/schemas.py`
- [ ] `regradar/backend/src/tests/test_concurrency.py`
- [ ] `migrations/versions/add_regulation_version.py`

**Steps:**
- [ ] Step 5.1 - Add `version` field to Regulation model
- [ ] Step 5.2 - Create migration for version field
- [ ] Step 5.3 - Update AI processing with pessimistic locking
- [ ] Step 5.4 - Add concurrent processing test
- [ ] Step 5.5 - Update API to return version

**Verification:**
- [ ] Version field added to model
- [ ] Migration applies successfully
- [ ] AI processing uses `with_for_update()`
- [ ] Concurrent test passes
- [ ] Version increments correctly
- [ ] API returns version

**Test:**
```bash
alembic upgrade head
pytest tests/test_concurrency.py::test_concurrent_ai_processing*

# Verify version in API
curl http://localhost:8000/api/regulations/1 | jq '.version'
```

**Commit:**
- [ ] Commit: `[RELIABILITY] Prevent race conditions in AI processing with pessimistic locking`

---

### Fix #6: Gemini Timeout Not Enforced

**Files to Modify:**
- [ ] `regradar/backend/src/ai/engine.py`
- [ ] `regradar/backend/src/config.py`
- [ ] `regradar/backend/src/scraper/runner.py`
- [ ] `regradar/backend/src/tests/test_ai_engine.py`

**Steps:**
- [ ] Step 6.1 - Add `asyncio.wait_for()` to Gemini API call
- [ ] Step 6.2 - Import asyncio module
- [ ] Step 6.3 - Add timeout validation to config
- [ ] Step 6.4 - Add timeout test
- [ ] Step 6.5 - Add graceful degradation for timeouts

**Verification:**
- [ ] `asyncio.wait_for()` wraps API call
- [ ] Timeout from config enforced
- [ ] API calls >30s fail fast
- [ ] Timeout test passes
- [ ] Graceful degradation on timeout

**Test:**
```bash
pytest tests/test_ai_engine.py::test_gemini*

# Test with slow API
# (Manually set timeout to 1s to test)
```

**Commit:**
- [ ] Commit: `[RELIABILITY] Enforce timeout on Gemini API calls`

---

### Fix #7: N+1 Query in Statistics Endpoint

**Files to Modify:**
- [ ] `regradar/backend/src/api/routes.py`
- [ ] `regradar/backend/src/tests/test_integration_load.py`

**Steps:**
- [ ] Step 7.1 - Replace in-memory domain counting with streaming
- [ ] Step 7.2 - Add batch processing for large datasets
- [ ] Step 7.3 - Add performance monitoring
- [ ] Step 7.4 - Add performance test
- [ ] Step 7.5 - Add caching (optional)

**Verification:**
- [ ] N+1 query eliminated
- [ ] Streaming approach used
- [ ] Memory usage constant
- [ ] Query time <500ms
- [ ] Performance test passes

**Test:**
```bash
# Load 10k regulations
# Test memory usage
time curl http://localhost:8000/api/stats

pytest tests/test_integration_load.py::test_stats_endpoint*
```

**Commit:**
- [ ] Commit: `[PERFORMANCE] Fix N+1 query in stats endpoint`

---

### Fix #13: No Request Timeout on External APIs

**Files to Modify:**
- [ ] `regradar/backend/src/scraper/base.py`
- [ ] `regradar/backend/src/scraper/sebi.py`
- [ ] `regradar/backend/src/scraper/rbi.py`

**Steps:**
- [ ] Verify timeout is enforced on all aiohttp calls
- [ ] Update SEBI scraper timeout (line 36)
- [ ] Update RBI scraper timeout (line 32)
- [ ] Test request timeout behavior

**Verification:**
- [ ] All aiohttp calls have timeout
- [ ] Timeout from config respected
- [ ] Timeout test passes

**Test:**
```bash
pytest tests/test_scraper.py -k "timeout"
```

**Commit:**
- [ ] Commit: `[RELIABILITY] Enforce timeout on scraper requests`

---

## PHASE 4: CODE QUALITY & MONITORING (2-3 hours)

### Fix #8: Console.log Statements in Production Code

**Files to Modify:**
- [ ] `regradar/frontend/src/utils/logger.ts` (create)
- [ ] `regradar/frontend/src/pages/FeedPage.tsx`
- [ ] `.eslintrc.json` (ESLint config)
- [ ] All React components

**Steps:**
- [ ] Step 8.1 - Create logger utility
- [ ] Step 8.2 - Update FeedPage to use logger
- [ ] Step 8.3 - Check all components for console.* calls
- [ ] Step 8.4 - Configure ESLint to forbid console
- [ ] Step 8.5 - Add optional backend logging endpoint

**Verification:**
- [ ] Logger utility created
- [ ] All console.* replaced with logger
- [ ] ESLint forbids console statements
- [ ] npm run lint passes
- [ ] npm run build succeeds
- [ ] No console.* in production

**Test:**
```bash
npm run lint
npm run build
grep -r "console\." src/ # Should return 0
```

**Commit:**
- [ ] Commit: `[SECURITY] Replace console.log with structured logging`

---

### Fix #9: Missing Rate Limiting

**Files to Modify:**
- [ ] `regradar/backend/src/main.py`
- [ ] `regradar/backend/src/api/routes.py`
- [ ] `regradar/backend/src/config.py`
- [ ] `regradar/backend/src/tests/test_security.py`
- [ ] `requirements.txt`

**Steps:**
- [ ] Step 9.1 - Install slowapi
- [ ] Step 9.2 - Configure rate limiter in main.py
- [ ] Step 9.3 - Apply limits to public endpoints
- [ ] Step 9.4 - Apply different limits per endpoint
- [ ] Step 9.5 - Add rate limit headers to responses
- [ ] Step 9.6 - Add configuration to settings
- [ ] Step 9.7 - Add test for rate limiting

**Verification:**
- [ ] slowapi installed
- [ ] Limiter configured
- [ ] Exception handler added
- [ ] All endpoints have limits
- [ ] Limits configurable
- [ ] Rate limit test passes
- [ ] Headers in responses

**Test:**
```bash
pip install slowapi
pytest tests/test_security.py::test_rate_limiting*

# Manual test
for i in {1..35}; do curl http://localhost:8000/api/regulations; done
# Last 5 should return 429
```

**Commit:**
- [ ] Commit: `[SECURITY] Add rate limiting to API endpoints`

---

### Fix #10: Incomplete Error Handling in Scrapers

**Files to Modify:**
- [ ] `regradar/backend/src/scraper/sebi.py`
- [ ] `regradar/backend/src/scraper/rbi.py`
- [ ] `regradar/backend/src/tests/test_scraper.py`

**Steps:**
- [ ] Add try-catch for network errors
- [ ] Add try-catch for timeouts
- [ ] Add try-catch for HTML parsing failures
- [ ] Add logging for all error paths
- [ ] Add tests for error conditions

**Verification:**
- [ ] All network operations wrapped in try-catch
- [ ] Timeouts handled gracefully
- [ ] Parsing errors don't crash scraper
- [ ] Errors logged with context

**Test:**
```bash
pytest tests/test_scraper.py -k "error"
```

**Commit:**
- [ ] Commit: `[RELIABILITY] Add comprehensive error handling to scrapers`

---

### Fix #11: Missing Input Validation on Pagination

**Files to Modify:**
- [ ] `regradar/backend/src/api/routes.py`
- [ ] `regradar/backend/src/tests/test_api.py`

**Steps:**
- [ ] Validate limit/offset before database query
- [ ] Add bounds checking
- [ ] Add test cases for edge cases

**Verification:**
- [ ] Limit validated (1-100)
- [ ] Offset validated (>=0)
- [ ] Large offsets handled
- [ ] Edge cases tested

**Test:**
```bash
# Test invalid limit
curl "http://localhost:8000/api/regulations?limit=1000"  # Should fail or cap
curl "http://localhost:8000/api/regulations?limit=-1"    # Should fail
curl "http://localhost:8000/api/regulations?offset=-5"   # Should fail

pytest tests/test_api.py -k "pagination"
```

**Commit:**
- [ ] Commit: `[SECURITY] Add input validation for pagination parameters`

---

### Fix #15: Insufficient Logging on Security Events

**Files to Modify:**
- [ ] `regradar/backend/src/api/routes.py`
- [ ] `regradar/backend/src/api/dependencies.py`
- [ ] `regradar/backend/src/scraper/runner.py`
- [ ] `regradar/backend/src/ai/engine.py`

**Steps:**
- [ ] Add security context to login/session creation
- [ ] Add logging to authentication failures
- [ ] Add logging to API misuse (rate limits, validation errors)
- [ ] Add logging to data access (what, when, who)
- [ ] Ensure all logs include correlation ID

**Verification:**
- [ ] Security events logged
- [ ] Correlation IDs in all logs
- [ ] Sensitive data not logged
- [ ] Logs are searchable

**Commit:**
- [ ] Commit: `[OBSERVABILITY] Add security event logging`

---

### Fix #12: Unencrypted Database Backups

**Files to Modify:**
- [ ] `scripts/backup.sh` (if exists)
- [ ] Deployment guide

**Steps:**
- [ ] Add GPG encryption to backup files
- [ ] Document backup encryption procedure
- [ ] Test backup/restore cycle

**Verification:**
- [ ] Backups encrypted with GPG
- [ ] Encryption key stored separately
- [ ] Restore procedure tested

**Note:** Can defer to Phase 2 (not critical for MVP)

**Commit:**
- [ ] Commit: `[SECURITY] Add encryption to database backups`

---

## FINAL VERIFICATION

### All Fixes Complete Checklist

**Compilation & Build:**
- [ ] `npm run build` succeeds
- [ ] `npm run type-check` passes
- [ ] `npm run lint` passes (0 errors)
- [ ] Backend tests: `pytest` passes (80%+ coverage)

**Security:**
- [ ] No hardcoded secrets
- [ ] No SQL injection possible
- [ ] API authentication enforced
- [ ] Rate limiting active
- [ ] CORS properly configured

**Reliability:**
- [ ] Race conditions eliminated
- [ ] API timeouts enforced
- [ ] N+1 queries eliminated
- [ ] Error handling comprehensive
- [ ] Logging comprehensive

**Performance:**
- [ ] API response <500ms (p95)
- [ ] Feed load <2s
- [ ] Stats query <500ms
- [ ] No memory leaks

**Testing:**
- [ ] 80%+ code coverage
- [ ] All edge cases tested
- [ ] Security tests pass
- [ ] Load test passes (100 concurrent)
- [ ] E2E flows verified

### Deploy Checklist

**Pre-Deployment:**
- [ ] All 15 fixes tested locally
- [ ] PR review completed
- [ ] CI/CD pipeline passes
- [ ] Backup created

**Deployment:**
- [ ] Backend fixes deployed
- [ ] Frontend fixes deployed
- [ ] Smoke tests passed
- [ ] Logs monitored

**Post-Deployment:**
- [ ] Error rate <0.5%
- [ ] API response <500ms
- [ ] No security alerts
- [ ] User-facing no issues

---

## NOTES

- Total estimated time: 18.25 hours (with 2-person team: 10-12 hours)
- Start with Phase 1 (compilation) - blocks everything
- Phases 2-4 can be parallelized by team
- Each fix has independent rollback procedure
- All fixes are non-breaking changes

---

**Last Updated:** April 18, 2026  
**Owner:** Security & Engineering Team  
**Status:** READY FOR IMPLEMENTATION
