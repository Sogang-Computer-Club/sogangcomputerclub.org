# Backend Dockerfile - FastAPI 애플리케이션
# 멀티 스테이지 빌드: 빌드 도구는 최종 이미지에 포함되지 않음

# --- 빌드 스테이지 ---
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /code

# 의존성 파일 먼저 복사 (Docker 레이어 캐싱 최적화)
COPY ./pyproject.toml ./uv.lock ./README.md /code/

# Python 의존성 설치
RUN uv sync --frozen --no-cache --no-dev

# --- 프로덕션 스테이지 ---
FROM python:3.13-slim

# 보안: root가 아닌 전용 사용자로 실행
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /code

# 시스템 의존성 설치 (curl: health check용)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# uv 복사 (런타임에 uv run 사용)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 빌드 스테이지에서 가상환경 복사
COPY --from=builder --chown=appuser:appgroup /code/.venv /code/.venv
COPY --chown=appuser:appgroup ./pyproject.toml ./uv.lock ./README.md /code/

# 애플리케이션 코드 복사
COPY --chown=appuser:appgroup ./app /code/app

# 디렉토리 소유권 설정 후 appuser로 전환
RUN chown -R appuser:appgroup /code
USER appuser

EXPOSE 8000

# 헬스 체크 - 오케스트레이터(ECS, K8s)가 컨테이너 상태 판단에 사용
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
