# Backend Dockerfile - FastAPI 애플리케이션
FROM python:3.13-slim

# 보안: root가 아닌 전용 사용자로 실행
# 컨테이너 탈출 공격 시 피해 범위 제한
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /code

# 시스템 의존성 설치 (curl: health check용)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# uv 패키지 매니저 설치 (pip보다 빠름)
RUN pip install --no-cache-dir uv

# 의존성 파일 먼저 복사 (Docker 레이어 캐싱 최적화)
# 코드 변경 시 의존성 재설치 불필요
COPY --chown=appuser:appgroup ./pyproject.toml ./uv.lock ./README.md /code/

# Python 의존성 설치
RUN uv sync --frozen --no-cache

# 애플리케이션 코드 복사
COPY --chown=appuser:appgroup ./app /code/app
COPY --chown=appuser:appgroup ./alembic /code/alembic
COPY --chown=appuser:appgroup ./alembic.ini /code/alembic.ini

# 비루트 사용자로 전환
USER appuser

EXPOSE 8000

# 헬스 체크 - 오케스트레이터(ECS, K8s)가 컨테이너 상태 판단에 사용
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
