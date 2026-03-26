# 백엔드 개발 가이드

FastAPI 기반 백엔드 개발 방법을 설명합니다.

## 기술 스택

- **Python 3.13**: 최신 Python 버전
- **FastAPI**: 비동기 웹 프레임워크
- **SQLAlchemy 2.0**: 비동기 ORM
- **Pydantic**: 데이터 검증
- **uv**: 패키지 매니저 (pip 대체)

## 프로젝트 구조

| 경로 | 설명 |
|------|------|
| `app/main.py` | FastAPI 앱 진입점 |
| `app/core/config.py` | 환경 설정 |
| `app/core/database.py` | DB 연결 |
| `app/core/repository.py` | 추상 리포지토리 |
| `app/core/dependencies.py` | 공통 의존성 |
| `app/common/middleware.py` | 미들웨어 |
| `app/common/metrics.py` | Prometheus 메트릭 |
| `app/common/rate_limit.py` | 요청 속도 제한 |
| `app/events/publisher.py` | 이벤트 퍼블리셔 (NullEventPublisher 기본) |
| `app/events/dependencies.py` | 이벤트 의존성 |
| `app/memos/` | 메모 도메인 (models, schemas, repository, service, router, dependencies) |
| `app/health/router.py` | 헬스체크 |

## 새 도메인 추가하기

아래 예시는 "posts" 도메인을 추가하는 과정입니다. 기존 `app/memos/` 구조를 참고하세요.

### 1. 모델 정의

`app/posts/models.py` 파일을 생성합니다. `app.core.database`에서 `metadata`를 import한 뒤 `sa.Table()`로 테이블을 정의합니다. 기존 예시는 `app/memos/models.py`를 참고하세요.

일반적인 컬럼 구성:

| 컬럼 | 타입 | 비고 |
|------|------|------|
| `id` | `Integer` | primary_key |
| `title` | `String(200)` | nullable=False |
| `content` | `Text` | nullable=False |
| `author` | `String(100)` | |
| `created_at` | `DateTime` | server_default=now() |
| `updated_at` | `DateTime` | onupdate=now() |

> **주의**: DB 테이블 생성 시 모델 import가 필수입니다. metadata만 import하면 테이블이 등록되지 않습니다.

### 2. 스키마 정의

`app/posts/schemas.py` 파일을 생성합니다. Pydantic `BaseModel`을 상속하여 Create, Update, InDB 세 가지 스키마를 정의합니다.

| 스키마 | 용도 | 주요 필드 |
|--------|------|-----------|
| `PostCreate` | 생성 요청 | title (필수), content (필수) |
| `PostUpdate` | 수정 요청 | title (선택), content (선택) |
| `PostInDB` | 응답 모델 | id, title, content, author, created_at, updated_at |

InDB 스키마에는 `model_config = {"from_attributes": True}`를 설정합니다. 기존 예시는 `app/memos/schemas.py`를 참고하세요.

### 3. 리포지토리 구현

`app/posts/repository.py` 파일을 생성합니다. `app.core.repository.AbstractRepository`를 상속한 추상 클래스를 먼저 정의하고, 이를 구현하는 구체 클래스를 작성합니다.

구현해야 할 메서드:

| 메서드 | 설명 |
|--------|------|
| `get_by_id(id)` | 단건 조회 |
| `get_all(skip, limit)` | 목록 조회 (페이지네이션) |
| `create(entity)` | 생성 후 반환 |
| `update(id, data)` | 수정 후 반환 |
| `delete(id)` | 삭제 |

도메인별 추가 메서드(예: `get_by_author`)도 추상 클래스에 선언합니다. 기존 예시는 `app/memos/repository.py`를 참고하세요.

### 4. 서비스 구현

`app/posts/service.py` 파일을 생성합니다. 서비스는 리포지토리와 이벤트 퍼블리셔를 주입받아 비즈니스 로직을 처리합니다.

> **Note**: 이벤트 발행은 기본 비활성화됨 (`EVENT_BACKEND=null`).
> `NullEventPublisher`가 기본값이므로 이벤트 코드는 있어도 실제 발행되지 않습니다.
> Kafka 또는 SQS 활성화 시 해당 의존성 설치 필요.

서비스 클래스에서는 도메인 전용 예외(예: `PostNotFoundError`)를 정의하고, 리포지토리 호출 결과가 None이면 해당 예외를 발생시킵니다. 기존 예시는 `app/memos/service.py`를 참고하세요.

### 5. 의존성 정의

`app/posts/dependencies.py` 파일을 생성합니다. FastAPI의 `Depends`를 사용하여 리포지토리와 서비스의 의존성 주입 함수를 정의합니다.

- `get_post_repository`: DB 세션(`get_db`)을 주입받아 리포지토리 인스턴스 반환
- `get_post_service`: 리포지토리와 이벤트 퍼블리셔(`get_event_publisher`)를 주입받아 서비스 인스턴스 반환

기존 예시는 `app/memos/dependencies.py`를 참고하세요.

### 6. 라우터 구현

`app/posts/router.py` 파일을 생성합니다. `APIRouter(prefix="/posts", tags=["Posts"])`로 라우터를 만들고 엔드포인트를 정의합니다.

| 메서드 | 경로 | 설명 | Rate Limit |
|--------|------|------|------------|
| GET | `/` | 목록 조회 | - |
| GET | `/{post_id}` | 단건 조회 | - |
| POST | `/` | 생성 (201) | RATE_LIMIT_WRITE |

라우터에서는 서비스 예외를 `HTTPException`으로 변환합니다. Rate limit이 필요한 엔드포인트에는 `@limiter.limit(RATE_LIMIT_WRITE)` 데코레이터를 추가합니다. 기존 예시는 `app/memos/router.py`를 참고하세요.

### 7. 라우터 등록

`app/main.py`에서 새 라우터를 import한 뒤 `app.include_router(router, prefix="/v1")`으로 등록합니다.

### 8. 마이그레이션 생성

`uv run alembic revision --autogenerate -m "Add posts table"` 으로 마이그레이션을 생성하고 `uv run alembic upgrade head`로 적용합니다.

> **주의**: Alembic은 dev 의존성이므로 프로덕션 컨테이너에서는 사용 불가합니다. deploy-aws.yml은 Alembic 마이그레이션을 실행하지 않으므로 새 테이블은 수동 생성이 필요합니다.

## 에러 처리

### 커스텀 예외

각 도메인의 `service.py`에서 도메인별 예외를 정의합니다 (예: `PostNotFoundError`, `PostForbiddenError`).

### 라우터에서 처리

라우터 엔드포인트에서 서비스 메서드를 호출할 때 try/except로 도메인 예외를 잡아 적절한 HTTP 상태 코드의 `HTTPException`으로 변환합니다.

| 예외 | HTTP 상태 코드 |
|------|----------------|
| `NotFoundError` | 404 |
| `ForbiddenError` | 403 |

## 테스트

### 단위 테스트

테스트는 `tests/` 디렉토리에 작성하며 `unittest.mock.AsyncMock`으로 리포지토리와 이벤트 퍼블리셔를 모킹합니다.

테스트 작성 패턴:

1. `@pytest.fixture`로 mock 리포지토리, mock 퍼블리셔, 서비스 인스턴스를 준비
2. `@pytest.mark.asyncio`로 비동기 테스트 작성
3. mock 반환값을 설정하고 서비스 메서드를 호출하여 결과 검증
4. 예외 케이스는 `pytest.raises`로 검증

테스트 실행: `uv run pytest tests/ -v`

기존 테스트 예시는 `tests/` 디렉토리를 참고하세요.

## 다음 단계

- [API 레퍼런스](./api-reference.md) - API 명세
- [테스트 가이드](./testing.md) - 테스트 상세
