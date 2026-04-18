# RegRadar Memory Index
## Cross-Session Knowledge Base

This file indexes all persistent memory about RegRadar. Check these when starting a new session.

### Project Context
- [project_context.md](project_context.md) — Complete overview, stack, timeline, users
- [development_standards.md](development_standards.md) — Code quality, testing, security standards

### Development Progress
- [SESSION_RESUME_POINT.md](SESSION_RESUME_POINT.md) — **Resume here** - Complete snapshot for next session
- [PROGRESS_TRACKER.md](PROGRESS_TRACKER.md) — Daily progress tracking and metrics
- **Current Day:** Day 1 Complete, Day 2 Pending
- **Completed Features:** Database & Infrastructure (Day 1)
- **Known Issues:** None - Day 1 clean
- **Performance Metrics:** All targets exceeded (health: 6.68ms vs <100ms requirement)

### Technical Decisions
- Stack: Python FastAPI + React + SQLite → PostgreSQL
- AI: Gemini 2.0-Flash (chosen for speed & cost)
- Database: SQLite Phase 1 (zero setup), PostgreSQL Phase 3
- Frontend: React + Tailwind (professional appearance, responsive)
- Deployment: Vercel + Railway (zero-ops, auto-scale)

### User Feedback
- (Will collect feedback as product launches)
- Compliments: What users love
- Pain Points: Where they struggle
- Feature Requests: What's missing
- Bug Reports: Issues found by users

### Architecture Decisions
- **Authentication:** Session ID in localStorage (Phase 1), auth in Phase 2
- **Caching:** None in Phase 1, Redis in Phase 3 (for scale)
- **Email:** Not included in Phase 1, Phase 2 feature
- **Search:** Keyword search in Phase 2, full-text in Phase 3
- **Cross-references:** Detected in Phase 2 (relates_to, supersedes, amended_by)

### Known Constraints
- **Gemini API:** 1,500 rpm limit (manage with caching)
- **Government Websites:** Unreliable HTML (expect failures)
- **Timeline:** 2 weeks to MVP (strict)
- **Budget:** Free tiers only (Vercel, Railway, Google Cloud free tier)
- **Team:** Solo developer (ruthless scope prioritization)

### Testing Strategy
- **Unit Tests:** Core logic, validation, utilities (30%)
- **Integration Tests:** API↔DB, Scraper↔DB, AI↔Storage (50%)
- **E2E Tests:** Complete user flows (20%)
- **Target Coverage:** 80%+ before any launch

### Performance Targets
- Feed load: <2 seconds (first paint)
- API response: <500ms (p95)
- Database query: <200ms (p95)
- Frontend bundle: <200KB (gzipped)
- Uptime: 99.5%+

### Security Posture
- OWASP Top 10 coverage (input validation, no injection, XSS prevention)
- Secrets in .env (never in code)
- HTTPS only (HSTS headers)
- CORS restricted to frontend domain
- Rate limiting on API

### Monitoring & Alerting
- Sentry for error tracking
- JSON structured logging
- Health checks (/health endpoint)
- Metrics: response time, error rate, uptime
- Alerts: Error rate >1%, response >1s, scraper down >12h

### Phase Evolution
- **Phase 1 (MVP):** SEBI + RBI, feed, stats, responsive
- **Phase 2:** MCA + MeitY + Gazette, email digest, cross-refs
- **Phase 3:** Trend analysis, impact scoring, PostgreSQL, enterprise

### Team & Communication
- Solo developer (focus on ruthless prioritization)
- Claude as AI assistant (code + architecture + planning)
- Values: Correctness, completeness, edge cases, production focus
- Communication style: Direct, specific, provide context

### What's Working Well
- (Track as development progresses)
- Architecture is solid
- Technology stack is proven
- Timeline is realistic

### What Needs Attention
- (Track as development progresses)
- Scraper reliability (government websites are unpredictable)
- API quota management (Gemini rate limits)
- Performance under load (pagination, caching strategy)
- Mobile responsiveness (test on various viewports)

