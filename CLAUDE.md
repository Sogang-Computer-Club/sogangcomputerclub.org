# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Official website for Sogang University's Central Computer Club (SGCC). Built with FastAPI (backend) + SvelteKit (frontend) in a cloud-native Docker architecture with PostgreSQL, Redis, and Kafka.

## Development Commands

### Backend (Python 3.13 / uv)
```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all backend tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_memos.py -v

# Run with coverage
uv run pytest tests/ --cov=app --cov-report=html

# Run integration tests (requires Docker services running)
uv run pytest tests/integration/ -v
```

### Frontend (Node.js / npm)
```bash
cd frontend

# Install dependencies
npm install

# Run development server (proxies API to localhost:8000)
npm run dev

# Run tests
npm run test

# Run single test file
npm run test -- src/lib/components/Header.test.ts

# Type check
npm run check

# Production build
npm run build
```

### Database Migrations (Alembic)
```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one version
uv run alembic downgrade -1
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [backend|frontend|nginx]

# Access PostgreSQL
docker-compose exec postgres psql -U memo_user -d memo_app

# Access Redis CLI
docker-compose exec redis redis-cli
```

## Architecture

### Backend Structure (`app/`)
- `main.py` - FastAPI app with lifespan management (DB, Redis, Kafka initialization)
- `config.py` - Settings via pydantic-settings
- `database.py` - SQLAlchemy async engine and session factory
- `auth.py` - JWT authentication (PBKDF2-HMAC-SHA256 password hashing)
- `rate_limit.py` - Rate limiting config (slowapi)
- `metrics.py` - Prometheus metrics definitions
- `dependencies.py` - FastAPI dependency injection
- `models/` - SQLAlchemy ORM models
- `schemas/` - Pydantic request/response schemas
- `routers/` - API route handlers (`health.py`, `memos.py`)
- `services/` - External service integrations (Kafka)
- `middleware.py` - Custom middleware (Prometheus metrics)

### Frontend Structure (`frontend/src/`)
- `routes/` - SvelteKit file-based routing
  - `routes/api/calendar/` - Server-side Google Calendar proxy (keeps API key server-side)
- `lib/components/` - Reusable Svelte components with co-located `.test.ts` files
- `lib/utils/` - Utility functions
- `lib/api.ts` - Backend API client
- `lib/types/` - TypeScript type definitions

### Key Patterns
- Backend uses async/await throughout (asyncpg, aiokafka, redis.asyncio)
- Frontend uses Svelte 5 with TypeScript
- Frontend tests: components have co-located `.test.ts` files, route tests are in `src/__tests__/routes/`
- Backend tests separated into `tests/`, `tests/integration/`, `tests/load/`

## Gotchas

- **API proxy rewrite**: Frontend dev server proxies `/api/*` to `http://localhost:8000` and strips the `/api` prefix. A call to `/api/v1/memos` becomes `/v1/memos` on the backend.
- **API versioning**: All endpoints except `/health` and `/metrics` are versioned under `/v1` prefix.
- **CI test exclusions**: Backend CI only runs unit tests, excluding `tests/integration/` and `tests/load/` (require running Docker services).
- **Production startup validation**: App fails to start if `SECRET_KEY` is the default value or `DATABASE_URL` contains "changeme".
- **Auth required for writes**: Memo create/update/delete require JWT Bearer token. Read operations are public.
- **Rate limits**: Write endpoints: 30/min, Search: 60/min, Default: 100/min.

## Environment Setup

Copy `.env.example` to `.env` and configure:
- `DATABASE_URL` - PostgreSQL async connection string
- `REDIS_URL` - Redis connection URL
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker address
- `SECRET_KEY` - JWT signing key (generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"`)
- `CORS_ORIGINS` - Comma-separated allowed origins

For production, use GitHub Secrets instead of `.env` file.

## Ports
- Frontend dev: 5173 (Vite) / 3000 (Docker)
- Backend: 8000
- PostgreSQL: 5432 (internal) / 5433 (host)
- Redis: 6379 (internal) / 6381 (host)
- Kafka: 9092
