# 백엔드 개발 가이드

FastAPI 기반 백엔드 개발 방법을 설명합니다.

## 기술 스택

- **Python 3.13**: 최신 Python 버전
- **FastAPI**: 비동기 웹 프레임워크
- **SQLAlchemy 2.0**: 비동기 ORM
- **Pydantic**: 데이터 검증
- **uv**: 패키지 매니저 (pip 대체)

## 프로젝트 구조

```
app/
├── __init__.py
├── main.py                 # FastAPI 앱 진입점
├── core/                   # 공유 인프라
│   ├── config.py          # 환경 설정
│   ├── database.py        # DB 연결
│   ├── repository.py      # 추상 리포지토리
│   └── dependencies.py    # 공통 의존성
├── common/                 # 공통 유틸
│   ├── middleware.py      # 미들웨어
│   ├── metrics.py         # Prometheus 메트릭
│   └── rate_limit.py      # 요청 속도 제한
├── events/                 # 이벤트 발행 (선택적, 기본 비활성화)
│   ├── publisher.py       # 이벤트 퍼블리셔 (NullEventPublisher 기본)
│   └── dependencies.py
├── memos/                  # 메모 도메인
│   ├── models.py
│   ├── schemas.py
│   ├── repository.py
│   ├── service.py
│   ├── router.py
│   └── dependencies.py
└── health/                 # 헬스체크
    └── router.py
```

## 새 도메인 추가하기

### 1. 모델 정의

```python
# app/posts/models.py
import sqlalchemy as sa
from ..core.database import metadata

posts = sa.Table(
    "posts",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("title", sa.String(200), nullable=False),
    sa.Column("content", sa.Text, nullable=False),
    sa.Column("author", sa.String(100)),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
)
```

### 2. 스키마 정의

```python
# app/posts/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)

class PostInDB(BaseModel):
    id: int
    title: str
    content: str
    author: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
```

### 3. 리포지토리 구현

```python
# app/posts/repository.py
from abc import abstractmethod
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.repository import AbstractRepository
from .models import posts

class AbstractPostRepository(AbstractRepository[dict, int]):
    @abstractmethod
    async def get_by_author(self, author: str) -> List[dict]: ...

class PostRepository(AbstractPostRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[dict]:
        query = posts.select().where(posts.c.id == id)
        result = await self.session.execute(query)
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        query = posts.select().order_by(posts.c.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [dict(row) for row in result.mappings().all()]

    async def create(self, entity: dict) -> dict:
        query = posts.insert().values(**entity).returning(posts.c.id)
        result = await self.session.execute(query)
        created_id = result.scalar_one()
        await self.session.commit()
        return await self.get_by_id(created_id)

    async def update(self, id: int, data: dict) -> Optional[dict]:
        query = posts.update().where(posts.c.id == id).values(**data)
        await self.session.execute(query)
        await self.session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        query = posts.delete().where(posts.c.id == id)
        await self.session.execute(query)
        await self.session.commit()
        return True

    async def get_by_author(self, author: str) -> List[dict]:
        query = posts.select().where(posts.c.author == author)
        result = await self.session.execute(query)
        return [dict(row) for row in result.mappings().all()]
```

### 4. 서비스 구현

> **Note**: 이벤트 발행은 기본 비활성화됨 (`EVENT_BACKEND=null`).
> `NullEventPublisher`가 기본값이므로 이벤트 코드는 있어도 실제 발행되지 않습니다.
> Kafka 또는 SQS 활성화 시 해당 의존성 설치 필요.

```python
# app/posts/service.py
from typing import List
from .repository import AbstractPostRepository
from .schemas import PostCreate, PostUpdate
from ..events.publisher import AbstractEventPublisher

class PostNotFoundError(Exception):
    pass

class PostService:
    def __init__(
        self,
        repository: AbstractPostRepository,
        event_publisher: AbstractEventPublisher
    ):
        self.repository = repository
        self.event_publisher = event_publisher

    async def create_post(self, post: PostCreate, author: str) -> dict:
        entity = {
            "title": post.title,
            "content": post.content,
            "author": author,
        }
        created = await self.repository.create(entity)

        # 이벤트 발행 (EVENT_BACKEND=null이면 무시됨)
        await self.event_publisher.publish(
            "post-created",
            {"id": created["id"], "title": post.title}
        )
        return created

    async def get_post(self, post_id: int) -> dict:
        post = await self.repository.get_by_id(post_id)
        if post is None:
            raise PostNotFoundError(f"Post {post_id} not found")
        return post

    async def get_posts(self, skip: int = 0, limit: int = 100) -> List[dict]:
        return await self.repository.get_all(skip, limit)
```

### 5. 의존성 정의

```python
# app/posts/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_db
from ..events.dependencies import get_event_publisher
from ..events.publisher import AbstractEventPublisher
from .repository import AbstractPostRepository, PostRepository
from .service import PostService

async def get_post_repository(
    db: AsyncSession = Depends(get_db)
) -> AbstractPostRepository:
    return PostRepository(db)

async def get_post_service(
    repository: AbstractPostRepository = Depends(get_post_repository),
    event_publisher: AbstractEventPublisher = Depends(get_event_publisher)
) -> PostService:
    return PostService(repository, event_publisher)
```

### 6. 라우터 구현

```python
# app/posts/router.py
from fastapi import APIRouter, HTTPException, Depends, status, Request

from .schemas import PostCreate, PostUpdate, PostInDB
from .service import PostService, PostNotFoundError
from .dependencies import get_post_service
from ..common.rate_limit import limiter, RATE_LIMIT_WRITE

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.get("/", response_model=list[PostInDB])
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    service: PostService = Depends(get_post_service)
):
    return await service.get_posts(skip, limit)

@router.get("/{post_id}", response_model=PostInDB)
async def get_post(
    post_id: int,
    service: PostService = Depends(get_post_service)
):
    try:
        return await service.get_post(post_id)
    except PostNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=PostInDB, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMIT_WRITE)
async def create_post(
    request: Request,
    post: PostCreate,
    service: PostService = Depends(get_post_service),
):
    return await service.create_post(post, post.author)
```

### 7. 라우터 등록

```python
# app/main.py
from .posts.router import router as posts_router

app.include_router(posts_router, prefix="/v1")
```

### 8. 마이그레이션 생성

```bash
uv run alembic revision --autogenerate -m "Add posts table"
uv run alembic upgrade head
```

## 에러 처리

### 커스텀 예외

```python
class PostNotFoundError(Exception):
    pass

class PostForbiddenError(Exception):
    pass
```

### 라우터에서 처리

```python
@router.delete("/{post_id}")
async def delete_post(post_id: int, service: PostService = Depends(get_post_service)):
    try:
        await service.delete_post(post_id)
    except PostNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PostForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
```

## 테스트

### 단위 테스트 예시

```python
# tests/test_posts.py
import pytest
from unittest.mock import AsyncMock

from app.posts.service import PostService, PostNotFoundError
from app.posts.schemas import PostCreate

@pytest.fixture
def mock_repository():
    return AsyncMock()

@pytest.fixture
def mock_publisher():
    return AsyncMock()

@pytest.fixture
def service(mock_repository, mock_publisher):
    return PostService(mock_repository, mock_publisher)

@pytest.mark.asyncio
async def test_create_post(service, mock_repository, mock_publisher):
    mock_repository.create.return_value = {"id": 1, "title": "Test"}

    post = PostCreate(title="Test", content="Content")
    result = await service.create_post(post, "user@example.com")

    assert result["id"] == 1
    mock_publisher.publish.assert_called_once()

@pytest.mark.asyncio
async def test_get_post_not_found(service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(PostNotFoundError):
        await service.get_post(999)
```

## 다음 단계

- [API 레퍼런스](./api-reference.md) - API 명세
- [테스트 가이드](./testing.md) - 테스트 상세
