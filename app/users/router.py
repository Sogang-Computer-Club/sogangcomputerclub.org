"""
Authentication API endpoints.
Thin router that delegates to UserService.
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


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMIT_AUTH)
async def register(
    request: Request,
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Register a new user account."""
    try:
        return await service.register(user_data)
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except StudentIdAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
@limiter.limit(RATE_LIMIT_AUTH)
async def login(
    request: Request,
    credentials: UserLogin,
    service: UserService = Depends(get_user_service)
):
    """Authenticate user and return JWT token."""
    try:
        return await service.login(credentials)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AccountDeactivatedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
@limiter.limit(RATE_LIMIT_AUTH)
async def refresh_token(
    request: Request,
    current_user: dict = Depends(require_auth),
    service: UserService = Depends(get_user_service)
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
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserInDB)
@limiter.limit("60/minute")
async def get_current_user_info(
    request: Request,
    current_user: dict = Depends(require_auth),
    service: UserService = Depends(get_user_service)
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
            detail="Failed to get user info"
        )
