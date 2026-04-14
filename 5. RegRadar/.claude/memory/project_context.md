---
name: RegRadar Project Context
description: Complete project overview, technical stack, and current status
type: project
---

# RegRadar Project Context

## What We're Building
**RegRadar** is an AI-powered regulatory intelligence platform for India that monitors 5 regulatory sources (RBI, SEBI, MCA, MeitY, Gazette), summarizes changes with Google Gemini, and delivers personalized feeds to compliance professionals.

**This is a real product** meant to launch publicly and serve thousands of users. Not a demo or portfolio piece.

## Market & Users
- **Primary Users:** Compliance officers at banks, NBFCs, fintechs (50,000+ in India)
- **Secondary:** Chartered Accountants (1.5M+ CAs)
- **Problem:** India's regulations change 36 times/day; professionals waste 2-4 hours manually checking 5+ websites
- **Solution:** AI-powered feed surfacing relevant changes with plain-English summaries
- **Timeline:** MVP launch Q2 2026 (2 weeks from April 15)

## Technical Stack
- **Frontend:** React 18 + Tailwind CSS (Vite bundler)
- **Backend:** Python FastAPI (async)
- **AI:** Google Gemini 2.0-Flash API
- **Database:** SQLite (Phase 1) → PostgreSQL (Phase 3)
- **Deployment:** Vercel (frontend) + Railway/Render (backend)
- **Testing:** pytest + Vitest

## Development Status
**Phase 1 MVP Timeline:** 10 working days
- **Day 1:** ✅ COMPLETE - Database & Infrastructure
- Day 2-5: Backend feature development (scrapers, AI, API)
- Day 6-9: Frontend (feed, filters, detail page, stats)
- Day 10: Deployment, seed data, launch prep

**Progress:** 1/10 days complete (10%)

## Key Constraints
- **Solo Developer** - No team, limited bandwidth
- **Zero Compromise Quality** - Production-grade from day one
- **Tight Timeline** - 2 weeks to launch
- **Budget:** Free tiers only (no paid services)
- **Scope:** Phase 1 = SEBI + RBI only (MCA/MeitY in Phase 2)

## Critical Success Factors
1. Feed loads in <2 seconds (performance)
2. 80%+ test coverage (reliability)
3. Zero unhandled errors (robustness)
4. 99.5% uptime (availability)
5. WCAG AA accessibility (compliance)
6. Proper error attribution (regulatory compliance)
7. Comprehensive logging (debuggability)
8. Security hardened (OWASP)

## Database Schema (Phase 1)
```
regulations - Processed regulatory updates
user_preferences - User domain selections
scraper_runs - Scraper execution history
ai_processing_history - AI analysis audit trail
regulation_relationships - Cross-references (Phase 2)
email_digests - Email digest records (Phase 2)
```

## API Endpoints (Phase 1)
- GET /api/regulations (list with pagination & filters)
- GET /api/regulations/{id} (detail view)
- GET /api/feed (personalized feed by domain)
- GET /api/stats (dashboard statistics)
- POST /api/preferences (save domain selection)
- GET /api/domains (list domains with counts)
- POST /api/scrape (manual scraper trigger, admin only)

## Architectural Components
1. **Scraper Service** - Fetches from RBI, SEBI RSS feeds
2. **Deduplicator** - Prevents duplicate regulations
3. **AI Engine** - Gemini-based summarization & classification
4. **Database Layer** - SQLAlchemy ORM with transactions
5. **API Layer** - FastAPI with error handling & validation
6. **Frontend** - React SPA with infinite scroll & filtering
7. **Scheduler** - APScheduler for 6-hourly scraper runs
8. **Monitoring** - Structured JSON logging + Sentry

## Design Principles
- **Clarity over Cleverness** - Simple code that works
- **Explicit over Implicit** - No hidden side effects
- **Fail Safe** - Flag uncertain summaries for review vs. show wrong content
- **Attribution First** - Every regulation links to original source
- **Test-Driven** - Tests written before refactoring
- **Performance Conscious** - Measure everything
- **Monitoring-First** - Logging, alerting, health checks built in
- **Production-Grade** - Error handling for 40+ edge cases

## Regulatory Domains (Classification)
1. Banking & Payments (RBI)
2. Securities & Capital Markets (SEBI)
3. Corporate Law & Governance (MCA)
4. Data Privacy & Protection (DPDP/MeitY)
5. Tax & GST
6. Anti-Money Laundering / KYC
7. Digital Lending
8. Insurance (IRDAI)
9. Fintech & UPI

## Phase 1 → Phase 2 → Phase 3 Evolution
**Phase 1 (MVP):** SEBI + RBI, personalized feed, stats
**Phase 2:** MCA, MeitY, Gazette scrapers + email digest + cross-referencing
**Phase 3:** Advanced analytics, impact scoring, PostgreSQL, enterprise features

## Known Risks & Mitigations
- **Gemini API quota:** Monitor daily, implement caching
- **Website changes:** Robust error handling, fallbacks
- **Database performance:** Use indexes, pagination
- **Solo dev bottleneck:** Ruthless scope prioritization
- **Regulatory accuracy:** Always link to source, flag uncertain summaries
- **Performance:** Measure and optimize early

## Success Metrics (Launch)
- ✅ Feed loads <2 seconds
- ✅ API response <500ms
- ✅ 80%+ test coverage
- ✅ Zero critical bugs
- ✅ 99.5% uptime
- ✅ WCAG AA compliant
- ✅ All edge cases handled
- ✅ Monitoring configured

