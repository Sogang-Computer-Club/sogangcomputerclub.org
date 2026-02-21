"""
인증 API 엔드포인트.

보안 설계 원칙:
- Rate Limiting: 인증 엔드포인트는 브루트포스 공격의 주요 대상이므로 엄격한 제한 적용
- 에러 메시지: 공격자에게 힌트를 주지 않도록 일반적인 메시지 사용 (예: "이메일 또는 비밀번호가 잘못됨")
- WWW-Authenticate 헤더: 401 응답 시 RFC 6750 표준 준수
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request
import logging

from .schemas import UserCreate, UserLogin, UserInDB, Token
from .service import (
    UserService,
    EmailAlreadyExistsError,
    StudentIdAlreadyExistsError,
    InvalidCredentialsError,
    AccountDeactivatedError,
    UserNotFoundError,
)
from .dependencies import get_user_service, require_auth
from ..common.rate_limit import limiter, RATE_LIMIT_AUTH

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


# Rate Limit 설명: 회원가입은 봇에 의한 대량 계정 생성을 방지하기 위해 제한
@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMIT_AUTH)
async def register(
    request: Request,
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """Register a new user account."""
    try:
        return await service.register(user_data)
    # 409 Conflict: 리소스 충돌을 명시적으로 표현 (RESTful 관례)
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except StudentIdAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=Token)
@limiter.limit(RATE_LIMIT_AUTH)
async def login(
    request: Request,
    credentials: UserLogin,
    service: UserService = Depends(get_user_service),
):
    """Authenticate user and return JWT token."""
    try:
        return await service.login(credentials)
    except InvalidCredentialsError as e:
        # WWW-Authenticate 헤더: OAuth 2.0 Bearer Token 스펙(RFC 6750) 준수
        # 클라이언트에게 인증 방식을 알려줌
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 403 vs 401: 인증은 됐지만(토큰 유효) 접근 권한이 없는 경우 403
    except AccountDeactivatedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
@limiter.limit(RATE_LIMIT_AUTH)
async def refresh_token(
    request: Request,
    current_user: dict = Depends(require_auth),
    service: UserService = Depends(get_user_service),
):
    """Refresh JWT token for authenticated user."""
    try:
        user_email = current_user.get("sub")
        return await service.refresh_token(user_email)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.get("/me", response_model=UserInDB)
@limiter.limit("60/minute")
async def get_current_user_info(
    request: Request,
    current_user: dict = Depends(require_auth),
    service: UserService = Depends(get_user_service),
):
    """Get current authenticated user's information."""
    try:
        user_email = current_user.get("sub")
        return await service.get_user_by_email(user_email)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user info",
        )
