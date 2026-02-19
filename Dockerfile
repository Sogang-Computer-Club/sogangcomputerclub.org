FROM python:3.13-slim

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /code

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (for better caching)
COPY --chown=appuser:appgroup ./pyproject.toml ./uv.lock ./README.md /code/

# Install Python dependencies
RUN uv sync --frozen --no-cache

# Copy application code
COPY --chown=appuser:appgroup ./app /code/app
COPY --chown=appuser:appgroup ./alembic /code/alembic
COPY --chown=appuser:appgroup ./alembic.ini /code/alembic.ini

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
