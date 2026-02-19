"""
Rate limiting configuration using SlowAPI.
Provides request rate limiting to protect against abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse
from ipaddress import ip_address, ip_network, IPv4Network, IPv6Network
from typing import List, Union

# Trusted proxy networks (Docker internal, localhost)
# Only trust X-Forwarded-For from these networks
TRUSTED_PROXY_NETWORKS: List[Union[IPv4Network, IPv6Network]] = [
    ip_network("127.0.0.0/8"),      # Localhost
    ip_network("10.0.0.0/8"),       # Docker default
    ip_network("172.16.0.0/12"),    # Docker bridge networks
    ip_network("192.168.0.0/16"),   # Private networks
    ip_network("::1/128"),          # IPv6 localhost
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
    Get the real client IP, considering proxy headers.
    Only trusts proxy headers if request comes from a trusted proxy.
    Falls back to direct connection IP if no trusted proxy headers.
    """
    client_host = request.client.host if request.client else ""

    # Only trust proxy headers if request comes from trusted proxy
    if client_host and is_trusted_proxy(client_host):
        # Check common proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs; the first is the client
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

    # Fall back to direct connection IP
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


# Rate limit constants
RATE_LIMIT_DEFAULT = "100/minute"
RATE_LIMIT_AUTH = "10/minute"  # Stricter for auth endpoints
RATE_LIMIT_WRITE = "30/minute"  # For POST/PUT/DELETE operations
RATE_LIMIT_SEARCH = "60/minute"  # For search operations
