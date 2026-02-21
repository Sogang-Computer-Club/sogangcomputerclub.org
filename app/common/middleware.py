"""
애플리케이션 미들웨어.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match
import time
from .metrics import REQUEST_COUNT, REQUEST_DURATION


def get_path_template(request: Request) -> str:
    """
    실제 경로 대신 라우트 템플릿 반환.

    Prometheus 레이블의 고카디널리티(high cardinality) 문제 방지.
    - 문제: /memos/1, /memos/2, /memos/3... 각각 다른 레이블로 기록되면 메트릭 폭발
    - 해결: /memos/{memo_id} 템플릿으로 통합하여 집계 가능하게 함
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
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        return response
