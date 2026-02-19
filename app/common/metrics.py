"""
Prometheus metrics definitions.
"""
from prometheus_client import Counter, Histogram, Gauge

# HTTP request metrics
REQUEST_COUNT = Counter(
    'fastapi_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'fastapi_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Application metrics
MEMO_COUNT = Gauge(
    'memo_total',
    'Total number of memos in the database'
)

ACTIVE_CONNECTIONS = Gauge(
    'fastapi_active_connections',
    'Number of active database connections'
)
