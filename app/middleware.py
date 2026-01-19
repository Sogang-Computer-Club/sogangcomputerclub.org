"""
Custom middleware for the application.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
from .metrics import REQUEST_COUNT, REQUEST_DURATION


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware that collects Prometheus metrics for all requests."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        endpoint = request.url.path
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
