# Codebase Audit Report

**Project:** sogangcomputerclub.org
**Date:** 2026-03-26
**Auditor:** Claude Opus 4.6 (automated, 11 parallel workers)
**Scope:** Full codebase (FastAPI backend + SvelteKit 5 frontend + Infrastructure)

---

## Overall Score: 6.2 / 10

| Category | Worker | Score | Findings |
|---|---|---|---|
| Security | ln-621 | 7/10 | 1 CRITICAL, 1 HIGH, 4 MEDIUM, 5 LOW |
| Build & CI | ln-622 | 6/10 | 4 HIGH, 8 MEDIUM, 7 LOW |
| Code Principles (Backend) | ln-623 | 7/10 | 2 HIGH, 5 MEDIUM, 5 LOW |
| Code Principles (Frontend) | ln-623 | 4/10 | 2 CRITICAL, 5 HIGH, 10 MEDIUM, 13 LOW |
| Code Quality (Backend) | ln-624 | 7.5/10 | 1 HIGH, 4 MEDIUM, 7 LOW |
| Code Quality (Frontend) | ln-624 | 5/10 | 5 HIGH, 9 MEDIUM, 10 LOW |
| Dependencies | ln-625 | 6/10 | 4 HIGH, 7 MEDIUM, 4 LOW |
| Dead Code | ln-626 | 6/10 | 6 HIGH, 8 MEDIUM, 7 LOW |
| Observability | ln-627 | 5/10 | 3 HIGH, 7 MEDIUM, 6 LOW |
| Concurrency | ln-628 | 7/10 | 0 HIGH, 4 MEDIUM, 5 LOW |
| Lifecycle | ln-629 | 7/10 | 0 HIGH, 4 MEDIUM, 5 LOW |

---

## Executive Summary

The backend is well-architected (layered Repository pattern, proper DI, parameterized SQL, non-root Docker) but the frontend has accumulated significant technical debt. The single biggest systemic issue is a **partially removed authentication system** -- the backend auth was reverted but the frontend auth code (store, API functions, types, login/sign-up pages, tests) remains as dead code, creating confusion and broken flows.

### Strengths

1. **SQL injection prevention** -- All queries use SQLAlchemy parameterized queries; LIKE wildcards are properly escaped
2. **XSS prevention** -- All `{@html}` usage is guarded by DOMPurify.sanitize()
3. **Security headers** -- Comprehensive OWASP headers in both SvelteKit hooks and Nginx (HSTS, CSP, X-Frame-Options)
4. **Docker security** -- Both containers run as non-root users
5. **CI security pipeline** -- Trivy, TruffleHog, CodeQL, dependency review
6. **Clean backend architecture** -- Router -> Service -> Repository layering with FastAPI Depends
7. **Rate limiting** -- All endpoints protected; IP extraction correctly validates trusted proxies
8. **Production validation** -- Startup blocks if default credentials detected in non-debug mode
9. **Google API key protection** -- Calendar API key kept server-side via `$env/dynamic/private`

### Domain Health Summary

| Domain | Avg Score | Key Issues |
|---|---|---|
| Backend (app/) | 7.2 | Event publisher bug, TOCTOU races, over-provisioned pool |
| Frontend (frontend/src/) | 4.5 | Massive DRY violations, dead auth system, SSR crashes, non-functional pages |
| Infrastructure | 6.3 | Single-stage Dockerfile, Docker socket exposure, missing health check deps |

---

## Critical & High-Priority Findings

### CRITICAL

| # | Category | Location | Finding |
|---|---|---|---|
| C1 | Security | `app/memos/router.py` | **No authentication on any CRUD endpoint.** Anyone can create, update, delete memos. Backend auth was reverted (commit 9882620) but no replacement exists. |
| C2 | DRY | `MemoCard.svelte`, `MemoPlus.svelte`, `MarkdownEditor.svelte` | **Markdown rendering duplicated 3x** -- config, DOMPurify, highlight.js, debounce, and ~110 lines of CSS each. |
| C3 | DRY | `NavigationBar.svelte` | **Hardcodes all menu items** despite `navItems` config existing in `$lib/config/navigation.ts` (which MobileMenu uses correctly). |

### HIGH

| # | Category | Location | Finding |
|---|---|---|---|
| H1 | Bug | `app/events/dependencies.py:16` | **Event publisher attribute mismatch.** Checks `app.state.kafka` but lifespan stores as `app.state.event_publisher`. Fallback always triggers -- events silently discarded. |
| H2 | Dead Code | `alembic/env.py:16` | **Broken import** -- imports `users` model that doesn't exist. Blocks all database migrations. |
| H3 | Dead Code | Frontend auth system (7 files) | **Entire auth flow is dead code** -- API functions, types, AuthStore, login page, sign-up page, tests. Backend auth was removed but frontend wasn't cleaned up. |
| H4 | Security | `docker-compose.yml:110` | **Docker socket mounted in certbot container.** Grants full host-level Docker control if compromised. |
| H5 | Build | `Dockerfile` | **Single-stage build.** Build tools remain in production image. |
| H6 | Build | `docker-compose.yml:93-97` | **Wrong script paths.** Mounts `./nginx.sh` and `./certbot.sh` but files are at `scripts/`. |
| H7 | Build | `docker-compose.prod.yml:32-35` | **Hard dependency on Kafka** in prod compose, contradicting scale guidelines. |
| H8 | Dependencies | `pyproject.toml` | **3 unused Python deps:** `python-json-logger`, `email-validator`, `urllib3`. |
| H9 | Dependencies | `frontend/package.json` | **`jsdom` in production deps** (30+ MB) should be devDependency. |
| H10 | Observability | Entire codebase | **No structured logging.** `python-json-logger` declared but never used. Plain-text `basicConfig` only. |
| H11 | Observability | Entire codebase | **No request tracing / correlation IDs.** Cannot correlate log entries per request. |
| H12 | Observability | Entire codebase | **No alerting rules.** Prometheus collects data but nobody is notified. |
| H13 | Quality | `Calendar.svelte:15`, `feed/+page.svelte:11` | **SSR crash** -- `$state(window.innerWidth)` at module top level. `window` undefined during SSR. |
| H14 | Quality | `sign-up/+page.svelte` | **Non-functional page.** No form submission handler, no state binding, no API calls. |
| H15 | Quality | `hooks.server.ts` vs `+page.svelte` | **CSP blocks YouTube iframe** on home page. Missing `frame-src` directive. |
| H16 | DRY | `FeedCard.svelte` / `MobileFeedCard.svelte` | **Nearly identical components** with only layout differences. |
| H17 | DRY | `login/+page.svelte`, `sign-up/+page.svelte` | **Entire forms duplicated** for mobile vs desktop instead of responsive CSS. |
| H18 | Dead Code | `verify_db.py` | **Orphaned debug script** with hardcoded database passwords committed to repo. |

---

## Medium-Priority Findings

### Concurrency

| # | Location | Finding | Recommendation |
|---|---|---|---|
| M1 | `app/memos/service.py:75-100` | TOCTOU race in update/delete -- check-then-act with separate queries | Use `UPDATE...RETURNING` or check rowcount |
| M2 | `app/memos/repository.py:49,59,68` | Premature commit inside repository breaks transaction composability | Move commit to service layer |
| M3 | `app/common/metrics.py` | MEMO_COUNT gauge drifts from reality due to race conditions | Derive from DB periodically |
| M4 | `app/common/rate_limit.py:64` | In-memory rate limiter is per-process (safe with single worker only) | Document single-worker constraint |

### Build & Dependencies

| # | Location | Finding | Recommendation |
|---|---|---|---|
| M5 | `frontend/Dockerfile` | Uses `npm install` (non-deterministic) instead of `npm ci` | Use `npm ci` |
| M6 | `frontend/package.json` | `@types/marked` v5 stale (marked v16 ships own types) | Remove |
| M7 | `frontend/package.json` | `@types/dompurify` redundant (ships own types) | Remove |
| M8 | `frontend/package.json` | `happy-dom`, `@sveltejs/adapter-auto`, `@sveltejs/package`, `publint` unused | Remove |
| M9 | `frontend/package.json` | `marked-highlight` installed but never imported | Remove |
| M10 | `pyproject.toml` | Inconsistent version pinning (mix of `==` and `>=`) | Standardize on `>=` |
| M11 | `frontend/tsconfig.json` | TypeScript strict mode disabled | Enable `"strict": true` |

### Backend Code

| # | Location | Finding | Recommendation |
|---|---|---|---|
| M12 | `app/events/` | Entire Kafka/SQS/ABC event system is YAGNI per scale guidelines | Simplify to NullEventPublisher only |
| M13 | `app/core/repository.py` | Two-level abstract hierarchy for single concrete class | Flatten or remove AbstractRepository |
| M14 | `app/memos/router.py` | Repetitive try/except boilerplate across 6 endpoints | Extract shared exception handler |
| M15 | `app/core/database.py:17-18` | Connection pool oversized (30 max) for t3.micro/db.t3.micro | Reduce to pool_size=3, max_overflow=5 |

### Frontend Code

| # | Location | Finding | Recommendation |
|---|---|---|---|
| M16 | Multiple files | Magic numbers: `#AE1F1F`, `70px`, `896`, `500`, `300` repeated | Extract to CSS vars / constants |
| M17 | `Footer.svelte` | Personal phone numbers hardcoded | Move to config |
| M18 | `MemoCard.svelte` (296 lines) | Component handles display, editing, markdown, API, dialogs | Split into smaller components |
| M19 | `Calendar.svelte` | Fetches data in component instead of load function | Move to `+page.server.ts` |
| M20 | Multiple files | Mixed Svelte 4/5 event syntax (`on:click` vs `onclick`) | Migrate to Svelte 5 |
| M21 | `ImageSlider.svelte:64` | Typo: `dekstop:text-[20px]` (should be `desktop:`) | Fix typo |

### Lifecycle & Observability

| # | Location | Finding | Recommendation |
|---|---|---|---|
| M22 | `app/core/database.py:14` | Engine created at module import, not inside lifespan | Move to lifespan function |
| M23 | `docker-compose.yml:20-21` | No health-check-gated depends_on for postgres | Add healthcheck condition |
| M24 | `app/memos/router.py` | Error logs use `f"...{e}"` -- no stack traces | Use `exc_info=True` |
| M25 | Service + Repository layers | Zero logging in business logic and data access | Add structured logging |
| M26 | `deploy-aws.yml` | No Alembic migration in deploy pipeline | Add migration step |

---

## Cross-Domain Patterns

### Recurring Bug: Event Publisher Attribute Mismatch

Found by 3 workers independently (ln-623, ln-624, ln-628): `app/events/dependencies.py` checks `app.state.kafka` but the lifespan stores as `app.state.event_publisher`. This is the highest-confidence finding in the audit.

### Recurring Theme: Dead Authentication System

Found by 4 workers (ln-621, ln-623-frontend, ln-624-frontend, ln-626): The partially removed auth system is the largest source of dead code and confusion. It spans API functions, types, stores, tests, and two page routes.

### Recurring Theme: Frontend DRY Violations

Found by 3 workers (ln-623-frontend, ln-624-frontend, ln-626): Markdown rendering duplicated 3x, navigation hardcoded despite config, mobile/desktop markup duplicated instead of responsive CSS.

### Recurring Theme: Over-Provisioned Infrastructure

Found by 3 workers (ln-628, ln-629, ln-624-backend): Connection pool (30 max) is excessive for t3.micro. Single-worker constraint undocumented.

---

## Recommended Action Plan

### Phase 1: Critical Fixes (Immediate)

1. **Fix alembic import** -- Remove `users` from `alembic/env.py:16` (blocks all migrations)
2. **Fix event publisher attribute** -- Change `app.state.kafka` to `app.state.event_publisher` in `dependencies.py`
3. **Delete `verify_db.py`** -- Contains hardcoded passwords
4. **Add `frame-src` to CSP** -- YouTube iframe is blocked on home page
5. **Fix SSR crashes** -- Move `window.innerWidth` inside `onMount` in Calendar and Feed

### Phase 2: Dead Code Cleanup (Short-term)

6. **Remove dead auth system** -- Frontend auth API functions, types, AuthStore, login/sign-up pages, and tests
7. **Remove unused Python deps** -- `python-json-logger`, `email-validator`, `urllib3`, `greenlet`
8. **Remove unused Node deps** -- `happy-dom`, `@types/marked`, `@types/dompurify`, `marked-highlight`, `@sveltejs/adapter-auto`, `@sveltejs/package`, `publint`
9. **Remove Docker socket mount** from certbot container

### Phase 3: Frontend Refactoring (Medium-term)

10. **Extract shared markdown rendering** -- Single utility + CSS file for MemoCard/MemoPlus
11. **Refactor NavigationBar** to use `navItems` config
12. **Merge FeedCard/MobileFeedCard** into single responsive component
13. **Fix mobile/desktop duplication** in login, sign-up, footer
14. **Extract magic numbers** into CSS custom properties and constants

### Phase 4: Backend Improvements (Medium-term)

15. **Simplify event system** -- Remove Kafka/SQS code, keep NullEventPublisher only
16. **Enable structured logging** -- Wire up `python-json-logger` or remove dependency
17. **Reduce connection pool** to pool_size=3, max_overflow=5
18. **Add Prometheus alerting rules**
19. **Fix TOCTOU races** in service layer (use RETURNING or check rowcount)

### Phase 5: Build & CI (Lower priority)

20. **Convert Dockerfile to multi-stage build**
21. **Fix script paths** in docker-compose.yml
22. **Remove Kafka dependency** from docker-compose.prod.yml
23. **Enable TypeScript strict mode**
24. **Standardize on npm** (update CLAUDE.md) or migrate to pnpm

---

## Advisory Findings (Context-Validated)

The following findings were flagged by workers but are acceptable given the project's documented constraints:

- **In-memory rate limiter** -- Acceptable for single-worker t3.micro deployment (Scale Guidelines)
- **No Redis caching** -- Explicitly documented as unnecessary at club scale
- **Kafka/SQS event system exists** -- YAGNI but not harmful if left as-is (removal is optional)
- **`BaseHTTPMiddleware` usage** -- Acceptable for memo-sized payloads
- **Combined liveness/readiness health check** -- Acceptable for current scale

---

*Generated by automated codebase audit. Individual worker reports available in `docs/project/.audit/ln-620/2026-03-26/`.*
