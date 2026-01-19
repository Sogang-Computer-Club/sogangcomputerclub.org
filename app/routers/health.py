"""
Health check and metrics endpoints.
"""
from fastapi import APIRouter, Request
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, UTC
from typing import Dict, Any
import sqlalchemy
import logging

router = APIRouter(tags=["System"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """System health check endpoint."""
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
    if request.app.state.kafka and request.app.state.kafka.is_connected:
        health_status["services"]["kafka"] = "healthy"
    else:
        health_status["services"]["kafka"] = "unhealthy"
        health_status["status"] = "degraded"

    return health_status


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
