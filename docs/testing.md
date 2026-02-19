# 테스트 가이드

단위 테스트, 통합 테스트, 부하 테스트 방법을 설명합니다.

## 테스트 구조

```
sogangcomputerclub.org/
├── tests/                          # 백엔드 테스트
│   ├── conftest.py                # pytest 설정, fixtures
│   ├── test_memos.py              # 메모 단위 테스트
│   ├── test_auth.py               # 인증 단위 테스트
│   └── test_integration.py        # 통합 테스트
├── frontend/src/lib/
│   └── components/
│       ├── Header.svelte
│       ├── Header.test.ts         # 컴포넌트 테스트
│       └── ...
└── locustfile.py                  # 부하 테스트
```

## 백엔드 테스트 (pytest)

### 실행 방법

```bash
# 전체 테스트
uv run pytest tests/ -v

# 특정 파일
uv run pytest tests/test_memos.py -v

# 특정 테스트
uv run pytest tests/test_memos.py::test_create_memo -v

# 커버리지
uv run pytest tests/ --cov=app --cov-report=html
```

### 단위 테스트 작성

```python
# tests/test_memos.py
import pytest
from unittest.mock import AsyncMock

from app.memos.service import MemoService, MemoNotFoundError
from app.memos.schemas import MemoCreate


@pytest.fixture
def mock_repository():
    """리포지토리 Mock 객체 생성"""
    return AsyncMock()


@pytest.fixture
def mock_publisher():
    """이벤트 퍼블리셔 Mock 객체 생성"""
    return AsyncMock()


@pytest.fixture
def service(mock_repository, mock_publisher):
    """테스트용 서비스 인스턴스"""
    return MemoService(mock_repository, mock_publisher)


@pytest.mark.asyncio
async def test_create_memo(service, mock_repository, mock_publisher):
    """메모 생성 테스트"""
    # Arrange
    mock_repository.create.return_value = {
        "id": 1,
        "title": "Test",
        "content": "Content",
        "author": "user@test.com"
    }

    memo = MemoCreate(title="Test", content="Content")

    # Act
    result = await service.create_memo(memo, "user@test.com")

    # Assert
    assert result["id"] == 1
    assert result["title"] == "Test"
    mock_repository.create.assert_called_once()
    mock_publisher.publish.assert_called_once()


@pytest.mark.asyncio
async def test_get_memo_not_found(service, mock_repository):
    """존재하지 않는 메모 조회 시 예외 발생"""
    # Arrange
    mock_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(MemoNotFoundError):
        await service.get_memo(999)
```

### Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import metadata


@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 생성 (pytest-asyncio용)"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """테스트용 인메모리 SQLite 엔진"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """테스트용 DB 세션"""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_client(test_app):
    """FastAPI 테스트 클라이언트"""
    from httpx import AsyncClient
    return AsyncClient(app=test_app, base_url="http://test")
```

## 프론트엔드 테스트 (Vitest)

### 실행 방법

```bash
cd frontend

# 전체 테스트
npm run test

# 감시 모드 (파일 변경 시 자동 실행)
npm run test:watch

# 커버리지
npm run test:coverage

# UI 모드
npm run test:ui
```

### 컴포넌트 테스트 작성

```typescript
// lib/components/Button.test.ts
import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/svelte';
import Button from './Button.svelte';

describe('Button', () => {
    it('렌더링된다', () => {
        const { getByRole } = render(Button, {
            props: { children: () => 'Click me' }
        });

        expect(getByRole('button')).toBeInTheDocument();
    });

    it('클릭 시 핸들러가 호출된다', async () => {
        const handleClick = vi.fn();

        const { getByRole } = render(Button, {
            props: {
                onclick: handleClick,
                children: () => 'Click me'
            }
        });

        await fireEvent.click(getByRole('button'));

        expect(handleClick).toHaveBeenCalledOnce();
    });

    it('disabled 상태에서 클릭이 무시된다', async () => {
        const handleClick = vi.fn();

        const { getByRole } = render(Button, {
            props: {
                onclick: handleClick,
                disabled: true,
                children: () => 'Click me'
            }
        });

        await fireEvent.click(getByRole('button'));

        expect(handleClick).not.toHaveBeenCalled();
    });
});
```

### Context를 사용하는 컴포넌트 테스트

```typescript
// lib/components/AuthStatus.test.ts
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import AuthStatus from './AuthStatus.svelte';
import { AUTH_CONTEXT_KEY, AuthStore } from '$lib/stores/auth.svelte';

describe('AuthStatus', () => {
    it('로그인 상태를 표시한다', () => {
        // Context 제공
        const authStore = new AuthStore();
        authStore.token = 'test-token';
        authStore.user = { email: 'user@test.com', name: 'Test User' };

        const { getByText } = render(AuthStatus, {
            context: new Map([[AUTH_CONTEXT_KEY, authStore]])
        });

        expect(getByText('로그인됨')).toBeInTheDocument();
        expect(getByText('Test User')).toBeInTheDocument();
    });

    it('비로그인 상태를 표시한다', () => {
        const authStore = new AuthStore();

        const { getByText } = render(AuthStatus, {
            context: new Map([[AUTH_CONTEXT_KEY, authStore]])
        });

        expect(getByText('로그인')).toBeInTheDocument();
    });
});
```

### 비동기 테스트

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, waitFor } from '@testing-library/svelte';
import MemoList from './MemoList.svelte';

// API Mock
vi.mock('$lib/api', () => ({
    getMemos: vi.fn(() => Promise.resolve([
        { id: 1, title: 'Test Memo', content: 'Content' }
    ]))
}));

describe('MemoList', () => {
    it('메모 목록을 로드한다', async () => {
        const { getByText } = render(MemoList);

        // 비동기 로딩 대기
        await waitFor(() => {
            expect(getByText('Test Memo')).toBeInTheDocument();
        });
    });
});
```

## 통합 테스트

### Docker Compose로 실행

```bash
# 테스트용 서비스 실행
docker-compose -f docker-compose.test.yml up -d

# 통합 테스트 실행
uv run pytest tests/test_integration.py -v

# 정리
docker-compose -f docker-compose.test.yml down -v
```

### 통합 테스트 예시

```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_full_memo_workflow():
    """메모 CRUD 전체 흐름 테스트"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 회원가입
        register_response = await client.post("/v1/auth/register", json={
            "email": "test@sogang.ac.kr",
            "password": "password123",
            "name": "Test User",
            "student_id": "20231234"
        })
        assert register_response.status_code == 201

        # 2. 로그인
        login_response = await client.post("/v1/auth/login", json={
            "email": "test@sogang.ac.kr",
            "password": "password123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. 메모 생성
        create_response = await client.post("/v1/memos", json={
            "title": "Test Memo",
            "content": "Test Content"
        }, headers=headers)
        assert create_response.status_code == 201
        memo_id = create_response.json()["id"]

        # 4. 메모 조회
        get_response = await client.get(f"/v1/memos/{memo_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Test Memo"

        # 5. 메모 수정
        update_response = await client.put(f"/v1/memos/{memo_id}", json={
            "title": "Updated Memo"
        }, headers=headers)
        assert update_response.status_code == 200

        # 6. 메모 삭제
        delete_response = await client.delete(
            f"/v1/memos/{memo_id}",
            headers=headers
        )
        assert delete_response.status_code == 204
```

## 부하 테스트 (Locust)

### 설치

```bash
uv add locust
```

### 테스트 시나리오

```python
# locustfile.py
from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # 요청 간 대기 시간

    def on_start(self):
        """테스트 시작 시 로그인"""
        response = self.client.post("/v1/auth/login", json={
            "email": "test@sogang.ac.kr",
            "password": "password123"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @task(3)
    def view_memos(self):
        """메모 목록 조회 (빈도: 3)"""
        self.client.get("/v1/memos")

    @task(1)
    def create_memo(self):
        """메모 생성 (빈도: 1)"""
        if self.token:
            self.client.post("/v1/memos", json={
                "title": "Load Test Memo",
                "content": "Created during load test"
            }, headers=self.headers)

    @task(2)
    def search_memos(self):
        """메모 검색 (빈도: 2)"""
        self.client.get("/v1/memos/search?q=test")
```

### 실행

```bash
# Web UI로 실행
locust -f locustfile.py --host=http://localhost:8000

# CLI로 실행 (100 사용자, 10/초 증가, 60초 실행)
locust -f locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 60s --headless
```

### 결과 해석

| 메트릭 | 권장값 |
|--------|--------|
| Median Response Time | < 200ms |
| 95th Percentile | < 500ms |
| Requests/sec | 서버 사양에 따라 |
| Failure Rate | < 1% |

## CI/CD 테스트

### GitHub Actions 설정

```yaml
# .github/workflows/backend-ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db
        run: |
          uv sync
          uv run pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
```

## 테스트 모범 사례

### AAA 패턴

```python
async def test_example():
    # Arrange - 준비
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = {"id": 1}
    service = MyService(mock_repo)

    # Act - 실행
    result = await service.get_item(1)

    # Assert - 검증
    assert result["id"] == 1
    mock_repo.get_by_id.assert_called_once_with(1)
```

### 테스트 격리

- 각 테스트는 독립적으로 실행 가능해야 함
- 테스트 간 상태 공유 금지
- 외부 의존성은 Mock 처리

### 네이밍

```python
# ✓ 좋은 예: 동작을 설명
def test_create_memo_returns_created_memo():
def test_get_memo_raises_error_when_not_found():

# ✗ 나쁜 예: 의미 없는 이름
def test_memo1():
def test_function():
```

## 다음 단계

- [백엔드 개발](./backend.md) - 테스트 대상 코드
- [문제 해결](./troubleshooting.md) - 테스트 문제 해결

