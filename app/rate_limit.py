"""
Rate limiting configuration using SlowAPI.
Provides request rate limiting to protect against abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse


def get_real_client_ip(request: Request) -> str:
    """
    Get the real client IP, considering proxy headers.
    Falls back to direct connection IP if no proxy headers.
    """
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
