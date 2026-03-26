# 테스트 가이드

단위 테스트, 통합 테스트, 부하 테스트 방법을 설명합니다.

## 테스트 구조

백엔드 테스트는 `tests/` 디렉토리에, 프론트엔드 컴포넌트 테스트는 `frontend/src/lib/components/` 내 각 컴포넌트 옆에 위치합니다.

| 디렉토리/파일 | 역할 |
|---|---|
| `tests/conftest.py` | pytest 설정, fixtures |
| `tests/test_memos.py` | 메모 단위 테스트 |
| `tests/test_health.py` | 헬스체크 테스트 |
| `tests/integration/` | 통합 테스트 |
| `tests/load/` | 부하 테스트 |
| `frontend/src/lib/components/*.test.ts` | 컴포넌트 테스트 |

## 백엔드 테스트 (pytest)

### 실행 방법

| Command | Purpose |
|---|---|
| `uv run pytest tests/ -v` | 전체 테스트 |
| `uv run pytest tests/test_memos.py -v` | 특정 파일 |
| `uv run pytest tests/test_memos.py::test_create_memo -v` | 특정 테스트 |
| `uv run pytest tests/ --cov=app --cov-report=html` | 커버리지 리포트 |

### 단위 테스트 작성

단위 테스트는 AAA(Arrange-Act-Assert) 패턴을 따릅니다. 리포지토리와 이벤트 퍼블리셔는 `AsyncMock`으로 대체하여 서비스 로직만 검증합니다.

테스트 대상 서비스는 `MemoService`이며, Mock된 리포지토리와 퍼블리셔를 주입받아 생성합니다. 메모 생성 테스트에서는 리포지토리의 `create` 반환값을 설정한 뒤, 서비스의 `create_memo`를 호출하고 결과값과 Mock 호출 여부를 검증합니다. 존재하지 않는 메모 조회 시에는 `MemoNotFoundError` 예외 발생을 확인합니다.

전체 구현은 `tests/test_memos.py` 참조.

### Fixtures (conftest.py)

테스트용 Fixture는 `tests/conftest.py`에 정의되어 있습니다.

| Fixture | Scope | 설명 |
|---|---|---|
| `event_loop` | session | pytest-asyncio용 이벤트 루프 생성 |
| `test_engine` | session | 인메모리 SQLite 엔진 (aiosqlite). metadata로 테이블 자동 생성 |
| `test_session` | function | 테스트용 DB 세션. 각 테스트 후 rollback으로 격리 |
| `test_client` | function | httpx `AsyncClient` 기반 FastAPI 테스트 클라이언트 |

전체 구현은 `tests/conftest.py` 참조.

## 프론트엔드 테스트 (Vitest)

### 실행 방법

| Command | Purpose |
|---|---|
| `cd frontend && npm run test` | 전체 테스트 |
| `cd frontend && npm run test:watch` | 감시 모드 (파일 변경 시 자동 실행) |
| `cd frontend && npm run test:ui` | UI 모드 |

### 컴포넌트 테스트 작성

Svelte 컴포넌트 테스트는 `@testing-library/svelte`의 `render`와 `fireEvent`를 사용합니다. 기본적인 렌더링 확인, 클릭 핸들러 호출 검증, disabled 상태 동작 확인 등을 테스트합니다.

프론트엔드 컴포넌트 테스트 예시는 `frontend/src/lib/components/Header.test.ts` 참조.

### 비동기 테스트

API 호출이 포함된 컴포넌트는 `vi.mock`으로 API 모듈을 Mock하고, `waitFor`로 비동기 렌더링 완료를 대기한 뒤 결과를 검증합니다.

## 통합 테스트

### Docker Compose로 실행

| Command | Purpose |
|---|---|
| `docker compose -f deploy/docker-compose.yml up -d` | 테스트용 서비스 실행 |
| `uv run pytest tests/integration/ -v` | 통합 테스트 실행 |
| `docker compose -f deploy/docker-compose.test.yml down -v` | 정리 |

### 통합 테스트 작성

통합 테스트는 httpx `AsyncClient`로 FastAPI 앱에 직접 요청을 보내 CRUD 전체 흐름을 검증합니다. 메모 생성(POST) -> 조회(GET) -> 수정(PUT) -> 삭제(DELETE) 순서로 실행하며, 각 단계의 HTTP 상태 코드와 응답 본문을 확인합니다.

전체 구현은 `tests/integration/` 디렉토리 참조.

## 부하 테스트 (Locust)

### 설치

`uv add locust` 로 설치합니다.

### 테스트 시나리오

Locust의 `HttpUser`를 상속하여 시나리오를 작성합니다. 각 task에 빈도 가중치를 부여하여 실제 사용 패턴을 시뮬레이션합니다.

| Task | 빈도 | 설명 |
|---|---|---|
| `view_memos` | 3 | 메모 목록 조회 (GET /v1/memos) |
| `create_memo` | 1 | 메모 생성 (POST /v1/memos) |
| `search_memos` | 2 | 메모 검색 (GET /v1/memos/search?q=test) |

요청 간 대기 시간은 1~3초로 설정합니다.

### 실행

| Command | Purpose |
|---|---|
| `locust -f locustfile.py --host=http://localhost:8000` | Web UI로 실행 |
| `locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 60s --headless` | CLI로 실행 (100 사용자, 10/초 증가, 60초) |

### 결과 해석

| 메트릭 | 권장값 |
|---|---|
| Median Response Time | < 200ms |
| 95th Percentile | < 500ms |
| Requests/sec | 서버 사양에 따라 |
| Failure Rate | < 1% |

## CI/CD 테스트

### GitHub Actions 설정

> **중요:** CI 환경에서는 `DEBUG=true`를 설정해야 프로덕션 검증(DATABASE_URL 등)을 우회합니다.

CI 파이프라인은 PostgreSQL 15 서비스 컨테이너를 띄우고, uv로 의존성 설치 후 pytest를 실행합니다. 커버리지 결과는 XML로 출력하여 Codecov에 업로드합니다.

주요 환경변수:

| 환경변수 | 값 | 용도 |
|---|---|---|
| `DEBUG` | `"true"` | 프로덕션 검증 우회 |
| `DATABASE_URL` | `postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db` | 테스트 DB 연결 |

전체 워크플로우 설정은 `.github/workflows/backend-ci.yml` 참조.

## 테스트 모범 사례

### AAA 패턴

모든 테스트는 Arrange(준비) -> Act(실행) -> Assert(검증) 순서로 구성합니다. Mock 객체를 설정하고, 테스트 대상 메서드를 호출한 뒤, 반환값과 Mock 호출을 검증합니다.

### 테스트 격리

- 각 테스트는 독립적으로 실행 가능해야 함
- 테스트 간 상태 공유 금지
- 외부 의존성은 Mock 처리

### 네이밍

테스트 함수명은 동작을 설명해야 합니다. `test_create_memo_returns_created_memo`나 `test_get_memo_raises_error_when_not_found`처럼 무엇을 테스트하는지 명확히 드러내야 합니다. `test_memo1`이나 `test_function` 같은 의미 없는 이름은 피합니다.

## 다음 단계

- [백엔드 개발](./backend.md) - 테스트 대상 코드
- [문제 해결](./troubleshooting.md) - 테스트 문제 해결
