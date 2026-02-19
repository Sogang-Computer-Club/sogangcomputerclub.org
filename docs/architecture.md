# 시스템 아키텍처

프로젝트의 전체 시스템 구조와 설계 원칙을 설명합니다.

## 아키텍처 개요

```mermaid
flowchart TB
    subgraph Client["클라이언트"]
        Browser[웹 브라우저]
    end

    subgraph Frontend["프론트엔드 (SvelteKit)"]
        SSR[SSR/CSR]
        Components[컴포넌트]
        Stores[상태 관리]
    end

    subgraph Backend["백엔드 (FastAPI)"]
        Router[라우터]
        Service[서비스]
        Repository[리포지토리]
    end

    subgraph Data["데이터 레이어"]
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis)]
    end

    subgraph Messaging["메시징"]
        SQS[AWS SQS]
    end

    Browser --> SSR
    SSR --> Router
    Router --> Service
    Service --> Repository
    Repository --> PostgreSQL
    Service --> Redis
    Service --> SQS
```

## 설계 원칙

### 1. 도메인 주도 설계 (DDD)

백엔드는 도메인별로 모듈화되어 있습니다:

```
app/
├── core/           # 공유 인프라
├── memos/          # 메모 도메인
├── users/          # 사용자 도메인
├── health/         # 헬스체크
└── events/         # 이벤트 발행
```

각 도메인 모듈은 다음 구조를 따릅니다:

```
memos/
├── __init__.py
├── models.py       # 데이터베이스 모델
├── schemas.py      # Pydantic 스키마 (요청/응답)
├── repository.py   # 데이터 접근 계층
├── service.py      # 비즈니스 로직
├── router.py       # API 엔드포인트
└── dependencies.py # 의존성 주입
```

### 2. 레이어드 아키텍처

```mermaid
flowchart LR
    Router --> Service --> Repository --> Database
```

| 레이어 | 책임 | 예시 |
|--------|------|------|
| Router | HTTP 요청/응답 처리 | `@router.post("/memos/")` |
| Service | 비즈니스 로직 | 권한 검사, 이벤트 발행 |
| Repository | 데이터 접근 | CRUD 쿼리 실행 |

### 3. 의존성 주입 (DI)

FastAPI의 `Depends()`를 사용하여 의존성을 주입합니다:

```python
# dependencies.py
async def get_memo_service(
    repository: AbstractMemoRepository = Depends(get_memo_repository),
    event_publisher: AbstractEventPublisher = Depends(get_event_publisher)
) -> MemoService:
    return MemoService(repository, event_publisher)

# router.py
@router.post("/memos/")
async def create_memo(
    memo: MemoCreate,
    service: MemoService = Depends(get_memo_service),
    current_user: dict = Depends(require_auth)
):
    return await service.create_memo(memo, current_user["sub"])
```

### 4. 리포지토리 패턴

데이터베이스 구현을 추상화하여 테스트와 교체를 용이하게 합니다:

```python
# 추상 인터페이스
class AbstractMemoRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[dict]: ...

    @abstractmethod
    async def create(self, entity: dict) -> dict: ...

# 구현체
class MemoRepository(AbstractMemoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[dict]:
        query = memos.select().where(memos.c.id == id)
        result = await self.session.execute(query)
        return dict(result.mappings().first()) if result else None
```

## 프론트엔드 아키텍처

### Svelte 5 패턴

```mermaid
flowchart TB
    subgraph Layout["+layout.svelte"]
        Context[Context 제공]
    end

    subgraph Page["+page.svelte"]
        Component[컴포넌트]
    end

    subgraph Store["Stores"]
        AuthStore[AuthStore]
        UIStore[UIStore]
    end

    Layout --> Context
    Context --> Page
    Store --> Context
```

### 상태 관리

Svelte 5의 Runes를 사용한 클래스 기반 스토어:

```typescript
// lib/stores/auth.svelte.ts
export class AuthStore {
    token = $state<string | null>(null);
    user = $state<User | null>(null);
    isAuthenticated = $derived(!!this.token);

    setToken(token: string) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }
}

// Context API로 주입
export const AUTH_CONTEXT_KEY = Symbol('auth');
```

## 이벤트 기반 아키텍처

비즈니스 이벤트를 메시지 큐로 발행하여 서비스 간 결합도를 낮춥니다:

```mermaid
flowchart LR
    Service[MemoService] --> Publisher[EventPublisher]
    Publisher --> Queue[SQS/Kafka]
    Queue --> Consumer[이벤트 소비자]
```

### 이벤트 발행 추상화

```python
# 추상 인터페이스
class AbstractEventPublisher(ABC):
    @abstractmethod
    async def publish(self, topic: str, message: dict) -> None: ...

# 구현체 선택 (환경변수로)
# EVENT_BACKEND=sqs  → SQSEventPublisher
# EVENT_BACKEND=kafka → KafkaEventPublisher
# EVENT_BACKEND=null  → NullEventPublisher (테스트용)
```

## 보안 아키텍처

### 인증 흐름

```mermaid
sequenceDiagram
    participant Client
    participant Frontend
    participant Backend
    participant DB

    Client->>Frontend: 로그인 요청
    Frontend->>Backend: POST /auth/login
    Backend->>DB: 사용자 조회
    Backend->>Backend: 비밀번호 검증 (PBKDF2)
    Backend->>Frontend: JWT 토큰 반환
    Frontend->>Frontend: localStorage 저장
    Frontend->>Client: 로그인 완료

    Note over Client,Backend: 이후 요청
    Client->>Frontend: API 요청
    Frontend->>Backend: Authorization: Bearer {token}
    Backend->>Backend: JWT 검증
    Backend->>Frontend: 응답
```

### 보안 설정

| 항목 | 설정 |
|------|------|
| 비밀번호 해싱 | PBKDF2-SHA256 (60만 회 반복) |
| 토큰 | JWT (HS256, 30분 만료) |
| CORS | 명시적 origin 목록 |
| Rate Limiting | 엔드포인트별 제한 |
| CSP | Content-Security-Policy 헤더 |

## 다음 단계

- [백엔드 개발](./backend.md) - 상세 개발 가이드
- [프론트엔드 개발](./frontend.md) - UI 개발 가이드
- [인프라 설정](./infrastructure.md) - AWS 아키텍처
