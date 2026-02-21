"""
사용자 도메인 의존성 주입.

인증 관련 의존성 포함:
- get_current_user: 선택적 인증 (비로그인 사용자도 허용)
- require_auth: 필수 인증 (미인증 시 401 반환)
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_db
from ..core.security import verify_token
from .repository import AbstractUserRepository, UserRepository
from .service import UserService

# auto_error=False: 토큰이 없어도 에러를 발생시키지 않음 (선택적 인증 지원)
security = HTTPBearer(auto_error=False)


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> AbstractUserRepository:
    """Dependency that provides the user repository."""
    return UserRepository(db)


async def get_user_service(
    repository: AbstractUserRepository = Depends(get_user_repository),
) -> UserService:
    """Dependency that provides the user service."""
    return UserService(repository)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """
    선택적 인증 - 토큰이 없어도 None 반환하고 계속 진행.

    사용 예: 비로그인 사용자도 볼 수 있지만 로그인 시 추가 기능 제공하는 엔드포인트
    """
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials)
    return payload


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """
    필수 인증 - 유효한 토큰이 없으면 401 에러 발생.

    반환값 payload 구조: {"sub": "user@email.com", "exp": 1234567890, ...}
    - sub: 사용자 이메일 (토큰 발급 시 설정)
    - exp: 토큰 만료 시간 (Unix timestamp)
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
