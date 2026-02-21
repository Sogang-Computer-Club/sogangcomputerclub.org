"""
FastAPI Memo Application - Main Entry Point

This is the main application module that wires together all components:
- Database connections
- API routers
- Prometheus metrics

Note: Redis와 Kafka/SQS 이벤트 시스템은 동아리 규모에서 불필요하여 제거됨.
Rate limiting은 in-memory storage를 사용함.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import sqlalchemy

from slowapi.errors import RateLimitExceeded

from .core.config import get_settings
from .core.database import engine, async_session_factory
from .routers import health_router, memos_router, auth_router
from .common.middleware import PrometheusMiddleware
from .events.publisher import create_event_publisher
from .common.metrics import MEMO_COUNT, ACTIVE_CONNECTIONS
from .common.rate_limit import limiter, rate_limit_exceeded_handler

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


# --- Background Tasks ---
async def monitor_database_connections(app: FastAPI):
    """Background task to monitor database connection pool."""
    while True:
        try:
            if hasattr(app.state, "db_engine"):
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
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                sqlalchemy.text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
                )
            )
            has_alembic = result.scalar()
            if not has_alembic:
                logger.warning(
                    "Lifespan: Alembic version table not found. Run 'alembic upgrade head' to apply migrations."
                )
            else:
                result = await conn.execute(
                    sqlalchemy.text("SELECT version_num FROM alembic_version")
                )
                version = result.scalar()
                logger.info(f"Lifespan: Database migration version: {version}")
    except Exception as e:
        logger.error(f"Lifespan: Database connection check failed - {e}")

    # Initialize Event Publisher (defaults to NullEventPublisher)
    event_publisher = create_event_publisher()
    try:
        await event_publisher.start()
        app.state.event_publisher = event_publisher
        logger.info(
            f"Lifespan: Event Publisher 초기화 완료 (backend: {settings.event_backend})"
        )
    except Exception as e:
        logger.warning(f"Lifespan: Event Publisher 초기화 실패 - {e}")
        app.state.event_publisher = None

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

    if app.state.event_publisher:
        await app.state.event_publisher.stop()
        logger.info("Lifespan: Event Publisher 종료 완료")

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
    description="FastAPI, SQLAlchemy 2.0을 사용한 비동기 메모 애플리케이션",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Rate Limiting ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# --- Middleware ---
app.add_middleware(PrometheusMiddleware)

# CORS configuration with explicit origins (not wildcard)
allowed_origins = settings.cors_origins_list
if settings.debug:
    allowed_origins = list(
        set(
            allowed_origins
            + [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]
        )
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# --- Routers ---
# Health router at root level (not versioned)
app.include_router(health_router)

# API v1 routers
API_V1_PREFIX = "/v1"
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(memos_router, prefix=API_V1_PREFIX)


# --- Development Server ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
