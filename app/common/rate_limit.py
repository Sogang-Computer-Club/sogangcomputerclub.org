"""
요청 속도 제한 (Rate Limiting) 설정.

SlowAPI를 사용하여 API 남용 방지.
프록시 환경(Nginx, Docker)에서 실제 클라이언트 IP를 정확히 식별해야 함.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse
from ipaddress import ip_address, ip_network, IPv4Network, IPv6Network
from typing import List, Union

# 신뢰할 수 있는 프록시 네트워크 대역
# 이 대역에서 오는 요청만 X-Forwarded-For 헤더를 신뢰함
# 외부에서 직접 X-Forwarded-For를 조작하여 IP 스푸핑하는 것을 방지
TRUSTED_PROXY_NETWORKS: List[Union[IPv4Network, IPv6Network]] = [
    ip_network("127.0.0.0/8"),      # 로컬호스트
    ip_network("10.0.0.0/8"),       # Docker 기본 네트워크
    ip_network("172.16.0.0/12"),    # Docker 브리지 네트워크
    ip_network("192.168.0.0/16"),   # 프라이빗 네트워크
    ip_network("::1/128"),          # IPv6 로컬호스트
]


def is_trusted_proxy(ip_str: str) -> bool:
    """Check if an IP address belongs to a trusted proxy network."""
    try:
        ip = ip_address(ip_str)
        return any(ip in network for network in TRUSTED_PROXY_NETWORKS)
    except ValueError:
        return False


def get_real_client_ip(request: Request) -> str:
    """
    실제 클라이언트 IP 추출.

    프록시 환경에서의 IP 추출 로직:
    1. 요청이 신뢰할 수 있는 프록시(Nginx, Docker)에서 왔는지 확인
    2. 신뢰 프록시라면 X-Forwarded-For 또는 X-Real-IP 헤더에서 IP 추출
    3. 아니라면 직접 연결된 IP 사용 (스푸핑 방지)
    """
    client_host = request.client.host if request.client else ""

    # 신뢰 프록시에서 온 요청만 프록시 헤더 참조
    if client_host and is_trusted_proxy(client_host):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For: "클라이언트, 프록시1, 프록시2" 형태
            # 첫 번째 IP가 원본 클라이언트
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

    # 프록시를 거치지 않은 직접 연결
    return get_remote_address(request)


# Create limiter instance with custom key function
limiter = Limiter(key_func=get_real_client_ip)


async def rate_limit_exceeded_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    detail = getattr(exc, 'detail', 'Rate limit exceeded')
    retry_after = getattr(exc, 'retry_after', 60)

    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
            "retry_after": str(detail)
        },
        headers={
            "Retry-After": str(retry_after)
        }
    )


# 엔드포인트별 요청 제한 설정
RATE_LIMIT_DEFAULT = "100/minute"   # 일반 조회 (GET)
RATE_LIMIT_AUTH = "10/minute"       # 인증 (로그인/회원가입) - 브루트포스 방지
RATE_LIMIT_WRITE = "30/minute"      # 쓰기 작업 (POST/PUT/DELETE)
RATE_LIMIT_SEARCH = "60/minute"     # 검색 - DB 부하 고려
