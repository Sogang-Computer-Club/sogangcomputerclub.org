import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.dependencies import get_db
from app.database import metadata
from app.auth import create_access_token
from typing import AsyncGenerator


# Test database URL (using SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield engine

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_factory(test_engine):
    """Create a test session factory"""
    return async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
        class_=AsyncSession
    )


@pytest_asyncio.fixture(scope="function")
async def test_db(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session"""
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_engine, test_session_factory):
    """Create a test client with overridden dependencies"""

    # Override the get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db

    # Override app state for testing
    app.state.db_engine = test_engine
    app.state.db_session_factory = test_session_factory
    app.state.redis = None  # Disable Redis for tests
    app.state.kafka = None  # Disable Kafka for tests

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def auth_token() -> str:
    """Create a test authentication token"""
    return create_access_token({
        "sub": "test@example.com",  # Email used as subject for ownership checks
        "user_id": 1,
        "is_admin": False
    })


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Create authorization headers with test token"""
    return {"Authorization": f"Bearer {auth_token}"}
