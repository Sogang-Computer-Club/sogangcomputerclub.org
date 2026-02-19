"""
Custom middleware for the application.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
import time
from .metrics import REQUEST_COUNT, REQUEST_DURATION


def get_path_template(request: Request) -> str:
    """
    Get the route template instead of the actual path.
    This prevents high cardinality in Prometheus labels.

    Example: /memos/123 -> /memos/{memo_id}
    """
    for route in request.app.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return route.path
    return request.url.path


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware that collects Prometheus metrics for all requests."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        # Use route template instead of raw path to prevent high cardinality
        endpoint = get_path_template(request)
        method = request.method
        status_code = response.status_code

        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        return response
