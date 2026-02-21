"""
Prometheus 메트릭 정의.

메트릭 타입:
- Counter: 단조 증가 값 (요청 수, 에러 수)
- Histogram: 분포 측정 (응답 시간 - p50, p90, p99 계산 가능)
- Gauge: 현재 상태 값 (활성 커넥션 수, 메모 수)
"""

from prometheus_client import Counter, Histogram, Gauge

# HTTP 요청 메트릭
REQUEST_COUNT = Counter(
    "fastapi_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "fastapi_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

# 애플리케이션 비즈니스 메트릭
MEMO_COUNT = Gauge("memo_total", "Total number of memos in the database")

ACTIVE_CONNECTIONS = Gauge(
    "fastapi_active_connections", "Number of active database connections"
)
