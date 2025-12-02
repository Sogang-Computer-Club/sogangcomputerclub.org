import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI, HTTPException, Depends, status, Request, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, ConfigDict
from typing import List, AsyncGenerator, Optional, Dict, Any
from datetime import datetime, date, UTC
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import redis.asyncio as redis
from aiokafka import AIOKafkaProducer
import json
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import asyncio
import time

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# --- Prometheus Metrics ---
REQUEST_COUNT = Counter(
    'fastapi_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)
REQUEST_DURATION = Histogram(
    'fastapi_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)
MEMO_COUNT = Gauge(
    'memo_total',
    'Total number of memos in the database'
)
ACTIVE_CONNECTIONS = Gauge(
    'fastapi_active_connections',
    'Number of active database connections'
)


# --- Environment Configuration ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://memo_user:changeme@postgres:5432/memo_app"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

# --- Database Schema ---
metadata = sqlalchemy.MetaData()
memos = sqlalchemy.Table(
    "memos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("title", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("content", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("tags", sqlalchemy.JSON, nullable=True, default=[]),
    sqlalchemy.Column("priority", sqlalchemy.Integer, nullable=False, default=2, server_default="2"),
    sqlalchemy.Column("category", sqlalchemy.String(50), nullable=True),
    sqlalchemy.Column("is_archived", sqlalchemy.Boolean, nullable=False, default=False, server_default="0"),
    sqlalchemy.Column("is_favorite", sqlalchemy.Boolean, nullable=False, default=False, server_default="0"),
    sqlalchemy.Column("author", sqlalchemy.String(100), nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now()),
)

# --- Background Tasks ---
async def monitor_database_connections(app: FastAPI):
    while True:
        try:
            if hasattr(app.state, 'db_engine'):
                # Access the sync engine's pool to get connection stats
                pool = app.state.db_engine.sync_engine.pool
                ACTIVE_CONNECTIONS.set(pool.checkedout())
        except Exception as e:
            logger.error(f"Error monitoring DB connections: {e}")
        await asyncio.sleep(5)



# --- Application Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Lifespan: 애플리케이션 시작...")

    # Initialize Database Engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True
    )
    async_session_factory = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession
    )

    app.state.db_engine = engine
    app.state.db_session_factory = async_session_factory
    logger.info("Lifespan: 데이터베이스 리소스가 app.state에 저장되었습니다.")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    logger.info("Lifespan: 데이터베이스 테이블이 성공적으로 준비되었습니다.")

    # Initialize Redis
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Lifespan: Redis 연결 성공")
    except Exception as e:
        logger.warning(f"Lifespan: Redis 연결 실패 - {e}")
        app.state.redis = None

    # Initialize Kafka Producer
    try:
        kafka_producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await kafka_producer.start()
        app.state.kafka = kafka_producer
        logger.info("Lifespan: Kafka Producer 연결 성공")
    except Exception as e:
        logger.warning(f"Lifespan: Kafka 연결 실패 - {e}")
        app.state.kafka = None

    logger.info("Lifespan: 모든 서비스가 성공적으로 시작되었습니다.")

    # Initialize MEMO_COUNT
    try:
        async with engine.connect() as conn:
            result = await conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM memos"))
            count = result.scalar()
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
        await app.state.kafka.stop()
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prometheus Middleware ---
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    return response



# --- Pydantic Models ---
class MemoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="메모 제목")
    content: str = Field(..., min_length=1, description="메모 내용")
    tags: Optional[List[str]] = Field(default=[], description="태그 목록")
    priority: int = Field(default=2, ge=1, le=4, description="우선순위 (1:낮음, 2:보통, 3:높음, 4:긴급)")
    category: Optional[str] = Field(None, max_length=50, description="카테고리")
    is_archived: bool = Field(default=False, description="아카이브 여부")
    is_favorite: bool = Field(default=False, description="즐겨찾기 여부")
    author: Optional[str] = Field(None, max_length=100, description="작성자")

class MemoCreate(MemoBase):
    pass

class MemoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    priority: Optional[int] = Field(None, ge=1, le=4)
    category: Optional[str] = Field(None, max_length=50)
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None
    author: Optional[str] = Field(None, max_length=100)

class MemoInDB(MemoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Dependency Injection ---
async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# --- Health Check Endpoint ---
@app.get("/health", tags=["System"])
async def health_check(request: Request) -> Dict[str, Any]:
    """System health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "services": {}
    }

    # Check Database
    try:
        async with request.app.state.db_session_factory() as session:
            await session.execute(sqlalchemy.text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    if request.app.state.redis:
        try:
            await request.app.state.redis.ping()
            health_status["services"]["redis"] = "healthy"
        except Exception as e:
            health_status["services"]["redis"] = "unhealthy"
            health_status["status"] = "degraded"
            logger.error(f"Redis health check failed: {e}")
    else:
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"

    # Check Kafka
    if request.app.state.kafka:
        health_status["services"]["kafka"] = "healthy"
    else:
        health_status["services"]["kafka"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status


# --- Prometheus Metrics Endpoint ---
@app.get("/metrics", tags=["System"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
# --- Memo API Endpoints ---
@app.post("/memos/", response_model=MemoInDB, status_code=status.HTTP_201_CREATED, tags=["Memos"])
async def create_memo(memo: MemoCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """Create a new memo"""
    try:
        query = memos.insert().values(
            title=memo.title,
            content=memo.content,
            tags=memo.tags or [],
            priority=memo.priority,
            category=memo.category,
            is_archived=memo.is_archived,
            is_favorite=memo.is_favorite,
            author=memo.author
        ).returning(memos.c.id)
        result = await db.execute(query)
        created_id = result.scalar_one()
        await db.commit()
        created_memo_query = memos.select().where(memos.c.id == created_id)
        created_memo = await db.execute(created_memo_query)
        memo_data = created_memo.mappings().one()

        # Publish to Kafka
        if request.app.state.kafka:
            try:
                await request.app.state.kafka.send_and_wait(
                    "memo-created",
                    {"id": created_id, "title": memo.title, "action": "created"}
                )
            except Exception as e:
                logger.warning(f"Failed to publish to Kafka: {e}")

        return memo_data
    except Exception as e:
        await db.rollback()
        logger.error(f"메모 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 생성에 실패했습니다.")
    finally:
        if 'created_id' in locals():
             MEMO_COUNT.inc()


@app.get("/memos/", response_model=List[MemoInDB], tags=["Memos"])
async def read_memos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all memos"""
    try:
        query = memos.select().order_by(memos.c.id.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.mappings().all()
    except Exception as e:
        logger.error(f"메모 목록 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모를 불러오는 데 실패했습니다.")

@app.get("/memos/{memo_id}", response_model=MemoInDB, tags=["Memos"])
async def read_memo(memo_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific memo by ID"""
    try:
        query = memos.select().where(memos.c.id == memo_id)
        result = await db.execute(query)
        memo = result.mappings().first()
        if memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")
        return memo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 조회 중 오류가 발생했습니다.")

@app.put("/memos/{memo_id}", response_model=MemoInDB, tags=["Memos"])
async def update_memo(memo_id: int, memo: MemoUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    """Update a memo"""
    try:
        existing_memo_query = memos.select().where(memos.c.id == memo_id)
        existing_memo = (await db.execute(existing_memo_query)).mappings().first()
        if existing_memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        update_data = memo.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 내용이 없습니다.")

        query = memos.update().where(memos.c.id == memo_id).values(**update_data)
        await db.execute(query)
        await db.commit()

        updated_memo_query = memos.select().where(memos.c.id == memo_id)
        updated_memo = (await db.execute(updated_memo_query)).mappings().one()

        # Publish to Kafka
        if request.app.state.kafka:
            try:
                await request.app.state.kafka.send_and_wait(
                    "memo-updated",
                    {"id": memo_id, "action": "updated"}
                )
            except Exception as e:
                logger.warning(f"Failed to publish to Kafka: {e}")

        return updated_memo
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"메모(ID:{memo_id}) 수정 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 수정 중 오류가 발생했습니다.")

@app.delete("/memos/{memo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Memos"])
async def delete_memo(memo_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Delete a memo"""
    try:
        existing_memo_query = memos.select().where(memos.c.id == memo_id)
        existing_memo = (await db.execute(existing_memo_query)).mappings().first()
        if existing_memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        delete_query = memos.delete().where(memos.c.id == memo_id)
        await db.execute(delete_query)
        await db.commit()

        # Publish to Kafka
        if request.app.state.kafka:
            try:
                await request.app.state.kafka.send_and_wait(
                    "memo-deleted",
                    {"id": memo_id, "action": "deleted"}
                )
            except Exception as e:
                logger.warning(f"Failed to publish to Kafka: {e}")

        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"메모(ID:{memo_id}) 삭제 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 삭제 중 오류가 발생했습니다.")
    finally:
        if 'delete_query' in locals(): # Simple check if we reached the deletion point
             MEMO_COUNT.dec()


@app.get("/memos/search/", response_model=List[MemoInDB], tags=["Memos"])
async def search_memos(q: str = Query(..., min_length=1, description="검색어"), db: AsyncSession = Depends(get_db)):
    """Search memos by keyword"""
    try:
        search_query = f"%{q}%"
        query = memos.select().where(
            sqlalchemy.or_(
                memos.c.title.like(search_query),
                memos.c.content.like(search_query)
            )
        ).order_by(memos.c.id.desc())

        result = await db.execute(query)
        return result.mappings().all()
    except Exception as e:
        logger.error(f"메모 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 검색 중 오류가 발생했습니다.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
