"""
Authentication API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from ..schemas.user import UserCreate, UserLogin, UserInDB, Token
from ..models.user import users
from ..dependencies import get_db
from ..auth import hash_password, verify_password, create_access_token, require_auth
from ..rate_limit import limiter, RATE_LIMIT_AUTH

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMIT_AUTH)
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    try:
        # Check if email already exists
        existing_query = select(users).where(users.c.email == user_data.email)
        existing = await db.execute(existing_query)
        if existing.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Check if student_id already exists (if provided)
        if user_data.student_id:
            student_query = select(users).where(users.c.student_id == user_data.student_id)
            student_exists = await db.execute(student_query)
            if student_exists.first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Student ID already registered"
                )

        # Hash password and create user
        password_hash = hash_password(user_data.password)
        insert_query = users.insert().values(
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name,
            student_id=user_data.student_id,
        ).returning(users.c.id)

        result = await db.execute(insert_query)
        user_id = result.scalar_one()
        await db.commit()

        # Fetch created user
        user_query = select(users).where(users.c.id == user_id)
        user_result = await db.execute(user_query)
        user = user_result.mappings().one()

        logger.info(f"New user registered: {user_data.email}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
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
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    try:
        # Find user by email
        query = select(users).where(users.c.email == credentials.email)
        result = await db.execute(query)
        user = result.mappings().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if account is active
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        # Create access token
        token_data = {
            "sub": user["email"],
            "user_id": user["id"],
            "is_admin": user["is_admin"],
        }
        access_token = create_access_token(token_data)

        logger.info(f"User logged in: {credentials.email}")
        return Token(access_token=access_token)

    except HTTPException:
        raise
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
    db: AsyncSession = Depends(get_db)
):
    """Refresh JWT token for authenticated user."""
    try:
        # Verify user still exists and is active
        query = select(users).where(users.c.email == current_user.get("sub"))
        result = await db.execute(query)
        user = result.mappings().first()

        if not user or not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new access token
        token_data = {
            "sub": user["email"],
            "user_id": user["id"],
            "is_admin": user["is_admin"],
        }
        access_token = create_access_token(token_data)

        return Token(access_token=access_token)

    except HTTPException:
        raise
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
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user's information."""
    try:
        query = select(users).where(users.c.email == current_user.get("sub"))
        result = await db.execute(query)
        user = result.mappings().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user info"
        )
