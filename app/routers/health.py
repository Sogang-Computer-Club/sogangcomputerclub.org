"""
Health check and metrics endpoints.
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, UTC
from typing import Dict, Any
from ipaddress import ip_address, ip_network
import sqlalchemy
import logging

router = APIRouter(tags=["System"])
logger = logging.getLogger(__name__)

# Private network ranges (IPv4 and IPv6)
PRIVATE_NETWORKS = [
    ip_network("127.0.0.0/8"),      # IPv4 loopback
    ip_network("10.0.0.0/8"),       # Private Class A
    ip_network("172.16.0.0/12"),    # Private Class B
    ip_network("192.168.0.0/16"),   # Private Class C
    ip_network("::1/128"),          # IPv6 loopback
    ip_network("fc00::/7"),         # IPv6 unique local
    ip_network("fe80::/10"),        # IPv6 link-local
]


def _check_internal_access(request: Request) -> bool:
    """Check if request is from internal network using proper CIDR matching."""
    client_ip_str = request.headers.get("X-Real-IP", request.client.host if request.client else "")

    if not client_ip_str:
        return False

    try:
        client_ip = ip_address(client_ip_str)
        return any(client_ip in network for network in PRIVATE_NETWORKS)
    except ValueError:
        # Invalid IP address format
        logger.warning(f"Invalid IP address format: {client_ip_str}")
        return False


@router.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """
    System health check endpoint.
    Returns simple status for external requests, detailed info for internal requests.
    """
    is_internal = _check_internal_access(request)
    is_healthy = True

    # Check Database
    db_healthy = False
    try:
        async with request.app.state.db_session_factory() as session:
            await session.execute(sqlalchemy.text("SELECT 1"))
        db_healthy = True
    except Exception as e:
        is_healthy = False
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    redis_healthy = False
    if request.app.state.redis:
        try:
            await request.app.state.redis.ping()
            redis_healthy = True
        except Exception as e:
            is_healthy = False
            logger.error(f"Redis health check failed: {e}")
    else:
        is_healthy = False

    # Check Kafka
    kafka_healthy = request.app.state.kafka and request.app.state.kafka.is_connected
    if not kafka_healthy:
        is_healthy = False

    # Simple response for external requests
    if not is_internal:
        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.now(UTC).isoformat()
        }

    # Detailed response for internal requests
    return {
        "status": "healthy" if is_healthy else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "services": {
            "database": "healthy" if db_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
            "kafka": "healthy" if kafka_healthy else "unhealthy"
        }
    }


@router.get("/metrics")
async def metrics(request: Request):
    """
    Prometheus metrics endpoint.
    Only accessible from internal networks.
    """
    if not _check_internal_access(request):
        raise HTTPException(
            status_code=403,
            detail="Metrics endpoint is only accessible from internal networks"
        )
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
