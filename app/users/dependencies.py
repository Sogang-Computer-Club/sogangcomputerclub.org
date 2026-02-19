"""
User domain dependency injection.
Includes authentication dependencies.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_db
from ..core.security import verify_token
from .repository import AbstractUserRepository, UserRepository
from .service import UserService

security = HTTPBearer(auto_error=False)


async def get_user_repository(
    db: AsyncSession = Depends(get_db)
) -> AbstractUserRepository:
    """Dependency that provides the user repository."""
    return UserRepository(db)


async def get_user_service(
    repository: AbstractUserRepository = Depends(get_user_repository)
) -> UserService:
    """Dependency that provides the user service."""
    return UserService(repository)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    FastAPI dependency to get the current authenticated user.
    Returns None if no valid token is provided.

    Use this for optional authentication.
    """
    if credentials is None:
        return None

    payload = verify_token(credentials.credentials)
    return payload


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    FastAPI dependency that requires authentication.
    Raises HTTPException if no valid token is provided.

    Use this for endpoints that require authentication.
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
