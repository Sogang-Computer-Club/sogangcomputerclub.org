"""
FastAPI Memo Application - Main Entry Point

This is the main application module that wires together all components:
- Database connections
- Redis cache
- Kafka messaging
- API routers
- Prometheus metrics

The original monolithic code has been refactored into modular components.
See the original at main.py.backup if needed.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import redis.asyncio as redis
import sqlalchemy

from slowapi.errors import RateLimitExceeded

from .config import get_settings
from .database import engine, async_session_factory
from .routers import health_router, memos_router
from .middleware import PrometheusMiddleware
from .services.kafka import kafka_service
from .metrics import MEMO_COUNT, ACTIVE_CONNECTIONS
from .rate_limit import limiter, rate_limit_exceeded_handler

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


# --- Background Tasks ---
async def monitor_database_connections(app: FastAPI):
    """Background task to monitor database connection pool."""
    while True:
        try:
            if hasattr(app.state, 'db_engine'):
                pool = app.state.db_engine.sync_engine.pool
                ACTIVE_CONNECTIONS.set(pool.checkedout())
        except Exception as e:
            logger.error(f"Error monitoring DB connections: {e}")
        await asyncio.sleep(5)


# --- Application Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("Lifespan: 애플리케이션 시작...")

    # Store database resources in app state
    app.state.db_engine = engine
    app.state.db_session_factory = async_session_factory
    logger.info("Lifespan: 데이터베이스 리소스가 app.state에 저장되었습니다.")

    # Verify database connection and migration status
    # Note: Tables should be created via Alembic migrations, not auto-created here
    try:
        async with engine.connect() as conn:
            # Check if migrations have been applied
            result = await conn.execute(sqlalchemy.text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
            ))
            has_alembic = result.scalar()
            if not has_alembic:
                logger.warning("Lifespan: Alembic version table not found. Run 'alembic upgrade head' to apply migrations.")
            else:
                result = await conn.execute(sqlalchemy.text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                logger.info(f"Lifespan: Database migration version: {version}")
    except Exception as e:
        logger.error(f"Lifespan: Database connection check failed - {e}")

    # Initialize Redis
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Lifespan: Redis 연결 성공")
    except Exception as e:
        logger.warning(f"Lifespan: Redis 연결 실패 - {e}")
        app.state.redis = None

    # Initialize Kafka Producer
    try:
        await kafka_service.start()
        app.state.kafka = kafka_service
        logger.info("Lifespan: Kafka Producer 연결 성공")
    except Exception as e:
        logger.warning(f"Lifespan: Kafka 연결 실패 - {e}")
        app.state.kafka = None

    logger.info("Lifespan: 모든 서비스가 성공적으로 시작되었습니다.")

    # Initialize MEMO_COUNT
    try:
        async with engine.connect() as conn:
            result = await conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM memos"))
            count = result.scalar() or 0
            MEMO_COUNT.set(count)
            logger.info(f"Lifespan: MEMO_COUNT initialized to {count}")
    except Exception as e:
        logger.warning(f"Lifespan: Failed to initialize MEMO_COUNT - {e}")

    # Start Background Tasks
    monitoring_task = asyncio.create_task(monitor_database_connections(app))

    yield

    # Shutdown
    logger.info("Lifespan: 애플리케이션 종료 중...")

    if app.state.kafka:
        await kafka_service.stop()
        logger.info("Lifespan: Kafka Producer 종료 완료")

    if app.state.redis:
        await app.state.redis.aclose()
        logger.info("Lifespan: Redis 연결 종료 완료")

    monitoring_task.cancel()
    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass

    await app.state.db_engine.dispose()
    logger.info("Lifespan: 데이터베이스 연결 종료 완료")
    logger.info("Lifespan: 모든 서비스가 정상적으로 종료되었습니다.")


# --- FastAPI Application ---
app = FastAPI(
    title="Memo API",
    description="FastAPI, SQLAlchemy 2.0, Redis, Kafka를 사용한 비동기 메모 애플리케이션",
    version="1.0.0",
    lifespan=lifespan
)

# --- Rate Limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# --- Middleware ---
app.add_middleware(PrometheusMiddleware)

# CORS configuration with explicit origins (not wildcard)
allowed_origins = settings.cors_origins_list
if settings.debug:
    # In debug mode, also allow common development origins
    allowed_origins = list(set(allowed_origins + [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# --- Routers ---
app.include_router(health_router)
app.include_router(memos_router)


# --- Development Server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
