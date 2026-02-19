# 개발 환경 설정

로컬 개발 환경을 구축하는 방법을 설명합니다.

## 필수 요구사항

- **Python 3.13** 이상
- **Node.js 20** 이상
- **Docker** 및 **Docker Compose**
- **Git**

## 1. 프로젝트 클론

```bash
git clone https://github.com/Sogang-Computer-Club/sogangcomputerclub.org.git
cd sogangcomputerclub.org
```

## 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값들을 설정합니다:

```bash
# 데이터베이스
POSTGRES_USER=memo_user
POSTGRES_PASSWORD=your_secure_password    # 반드시 변경
POSTGRES_DB=memo_app

# Redis
REDIS_URL=redis://redis:6379

# Kafka (로컬 개발용)
KAFKA_BOOTSTRAP_SERVERS=kafka:9093
EVENT_BACKEND=kafka

# 보안
SECRET_KEY=your_secret_key_here           # 반드시 변경

# Grafana (선택)
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

## 3. 패키지 매니저 설치

### Backend: uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Frontend: npm

Node.js 20 이상이 설치되어 있으면 npm이 함께 설치됩니다.

## 4. 의존성 설치

```bash
# 백엔드 의존성
uv sync

# 프론트엔드 의존성
cd frontend
npm install
cd ..
```

## 5. 개발 서버 실행

### 방법 1: Docker Compose (권장)

모든 서비스를 한 번에 실행합니다.

```bash
docker-compose up -d
```

접속 주소:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서 (Swagger): http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090

로그 확인:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

서비스 중지:
```bash
docker-compose down

# 볼륨까지 삭제 (DB 초기화)
docker-compose down -v
```

### 방법 2: 개별 실행

데이터베이스와 Redis만 Docker로 실행하고 앱은 직접 실행합니다.

```bash
# 인프라 서비스만 실행
docker-compose up -d postgres redis kafka zookeeper

# 백엔드 실행 (새 터미널)
DATABASE_URL=postgresql+asyncpg://memo_user:your_password@localhost:5433/memo_app \
REDIS_URL=redis://localhost:6381 \
KAFKA_BOOTSTRAP_SERVERS=localhost:9092 \
uv run uvicorn app.main:app --reload --port 8000

# 프론트엔드 실행 (새 터미널)
cd frontend
npm run dev
```

## 6. 데이터베이스 마이그레이션

```bash
# 마이그레이션 적용
uv run alembic upgrade head

# 현재 버전 확인
uv run alembic current

# 새 마이그레이션 생성 (모델 변경 후)
uv run alembic revision --autogenerate -m "설명"
```

## 7. 개발 도구 설정

### VS Code 권장 확장

- **Python**: Python 언어 지원
- **Pylance**: 타입 체킹
- **Svelte for VS Code**: Svelte 지원
- **Tailwind CSS IntelliSense**: Tailwind 자동완성
- **Docker**: Docker 파일 지원
- **HashiCorp Terraform**: Terraform 지원

### VS Code settings.json

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },
  "svelte.enable-ts-plugin": true
}
```

## 8. 코드 스타일

### 백엔드 (Ruff)

```bash
# 린팅
uv run ruff check app/

# 자동 수정
uv run ruff check app/ --fix

# 포맷팅
uv run ruff format app/
```

### 프론트엔드

```bash
cd frontend

# 타입 체크
npm run check

# 린팅 (ESLint)
npm run lint
```

## 다음 단계

- [시스템 아키텍처](./architecture.md) - 전체 구조 이해
- [백엔드 개발](./backend.md) - API 개발 방법
- [프론트엔드 개발](./frontend.md) - UI 개발 방법
