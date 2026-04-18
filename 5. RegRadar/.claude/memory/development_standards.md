---
name: Development Quality Standards
description: Code quality, testing, error handling, and security requirements
type: project
---

# Development Quality Standards for RegRadar

## Code Quality (Non-Negotiable)

### Python Backend (PEP 8 + Black)
- Line length: 100 characters (Black default)
- Type hints: Mandatory for all functions
- Docstrings: Google style with Args, Returns, Raises
- No bare except clauses
- No hardcoded secrets
- No unstructured logging (print, console.log)

### JavaScript Frontend (ESLint + Prettier)
- Semicolons: Yes
- Trailing commas: Yes
- Line length: 100 characters
- React hooks only (no class components)
- Error boundaries for error handling
- PropTypes or TypeScript for validation

## Testing Standards

### Coverage Targets
- **Unit Tests:** 80%+ coverage
- **Integration Tests:** 50% of test suite
- **E2E Tests:** 20% of test suite
- **Error Paths:** 100% coverage

### Edge Cases (Must Test All)
**Scraper:**
- Empty feeds/tables
- Malformed HTML/XML
- Network timeouts (29s, 31s)
- Rate limit responses (429)
- Missing required fields
- Connection resets
- Certificate errors

**AI (Gemini):**
- Long documents (>5000 chars) - truncate
- Non-English text
- Missing required fields in response
- Invalid JSON (handle with validation)
- API quota exceeded
- Response timeout
- Invalid dates

**API:**
- Invalid session IDs
- Missing query parameters
- Massive pagination offsets (>1M)
- Concurrent requests
- Database connection loss
- Transaction rollbacks
- Empty result sets
- Malformed input

**Frontend:**
- Network disconnection
- Session expiration
- localStorage unavailable
- Very large result sets (1000+)
- Very small viewports (<320px)
- No JavaScript enabled
- Slow 3G network
- Malformed API responses

## Error Handling Requirements

### Structured Logging (JSON)
Every log must include context:
```python
logger.error(
    "AI analysis failed",
    extra={
        "regulation_id": 123,
        "source_body": "RBI",
        "processing_time_ms": 2500,
        "error_type": type(e).__name__,
        "error_message": str(e),
        "correlation_id": "req_abc123"
    }
)
```

### Graceful Degradation
- Scraper fails? Continue with other sources
- AI analysis fails? Flag as "review_pending" instead of showing wrong summary
- Database unavailable? Return 503, not 500
- Frontend API fails? Show error message, not blank screen
- Missing field? Use default/null, don't crash

### Retry Strategy
- Transient errors (5xx): 3 retries with exponential backoff
- Rate limits (429): Exponential backoff starting 5s
- Network timeouts: 2 retries with 5s delay
- Permanent errors (404, 403): Log and skip, don't retry

## Security Standards

### Input Validation
- Validate all inputs at API boundary (Pydantic)
- Check field types, lengths, formats
- Reject unknown fields
- Use regex for pattern matching
- Never trust user input

### Output Encoding
- React automatically escapes HTML (use this)
- Sanitize HTML if needed (DOMPurify)
- No dangerouslySetInnerHTML
- Encode special characters

### SQL Injection Prevention
- Never concatenate SQL queries
- Use parameterized queries (SQLAlchemy ORM)
- Use prepared statements for raw SQL
- Never use f-strings with user input

### Secret Management
- Environment variables only (.env files)
- Never commit secrets to git
- Secrets in .gitignore
- Use different keys for dev/staging/prod
- Rotate secrets regularly

### Authentication & Authorization (Phase 2)
- Use session tokens, not passwords (Phase 1)
- HTTPS only (enforce with HSTS)
- Secure cookies (HttpOnly, Secure flags)
- CSRF protection if needed
- Rate limiting to prevent brute force

## Performance Standards

### Response Time SLAs
| Component | Target | Measurement |
|-----------|--------|------------|
| Feed page load | <2s | First paint |
| API response | <500ms | p95 latency |
| Detail page | <1s | Page render |
| Search | <500ms | Results |
| Database query | <200ms | p95 |
| Frontend bundle | <200KB | Gzipped |

### Optimization Techniques
- Code splitting by route
- Lazy loading components
- React.memo for expensive components
- Database indexes on filtered columns
- Connection pooling
- Pagination (never load all)
- Caching (Redis for frequently accessed)

## Commit Standards

### Format
```
[PHASE#-DAY#-TASK] Brief subject (max 50 chars)

Detailed explanation of what and why (wrap at 72 chars).
Include context about the change and rationale.

Edge cases handled:
- Edge case 1
- Edge case 2

Testing:
- [x] Unit test
- [x] Integration test
- [x] Manual test

Performance:
- API response: XXms (p95)
- Database query: XXms
```

### Rules
- One logical change per commit
- Commits are atomic (don't break tests)
- Descriptive messages (not "fix" or "update")
- No merge commits (rebase instead)
- Sign commits with GPG (optional)

## Pre-Commit Checklist

### Code Quality
- [ ] Formatter passes (Black, Prettier)
- [ ] Linter passes (Pylint, ESLint)
- [ ] Type checks pass (mypy)
- [ ] No console.log/print in production code
- [ ] No hardcoded secrets
- [ ] No TODO/FIXME in critical paths

### Testing
- [ ] All new code has tests
- [ ] Tests pass locally
- [ ] Coverage maintained (80%+)
- [ ] Edge cases tested
- [ ] Error paths tested

### Security
- [ ] Input validation present
- [ ] No SQL injection risks
- [ ] No XSS vulnerabilities
- [ ] Secrets in .env
- [ ] No credentials in code

### Documentation
- [ ] Docstrings for functions
- [ ] Comments for non-obvious logic
- [ ] README updated if needed

## Pre-Merge Checklist (Pull Request)

- [ ] Peer review completed
- [ ] CI/CD pipeline passes
- [ ] Test coverage 80%+
- [ ] Manual testing done
- [ ] No regressions
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Documentation complete

## Deployment Checklist

- [ ] All features working
- [ ] No critical bugs
- [ ] Performance SLAs met
- [ ] Security audit complete
- [ ] Load testing passed
- [ ] Accessibility verified
- [ ] Monitoring configured
- [ ] Backup strategy tested

## What NOT to Do

❌ **Never:**
- Bare except clauses
- Hardcoded secrets
- Magic numbers/strings
- Silent errors (without logging)
- Untested code
- Unhandled edge cases
- SQL string concatenation
- dangerouslySetInnerHTML
- Cross-site requests without CORS
- Console logging in production
- TODOs in critical paths

## What ALWAYS Do

✅ **Always:**
- Validate inputs at boundaries
- Handle errors explicitly
- Log with context
- Test edge cases
- Use indexes on filtered columns
- Paginate results
- Compress responses
- Cache when possible
- Monitor in production
- Document non-obvious logic

