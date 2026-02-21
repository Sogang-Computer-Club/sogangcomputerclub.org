"""
User/Auth service containing business logic.
"""

import logging

from .repository import AbstractUserRepository
from .schemas import UserCreate, UserLogin, Token
from ..core.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)


class EmailAlreadyExistsError(Exception):
    """Raised when email is already registered."""

    pass


class StudentIdAlreadyExistsError(Exception):
    """Raised when student ID is already registered."""

    pass


class InvalidCredentialsError(Exception):
    """Raised when credentials are invalid."""

    pass


class AccountDeactivatedError(Exception):
    """Raised when account is deactivated."""

    pass


class UserNotFoundError(Exception):
    """Raised when user is not found."""

    pass


class UserService:
    """Service layer for user/auth operations."""

    def __init__(self, repository: AbstractUserRepository):
        self.repository = repository

    async def register(self, user_data: UserCreate) -> dict:
        """Register a new user."""
        # Check if email already exists
        if await self.repository.email_exists(user_data.email):
            raise EmailAlreadyExistsError("Email already registered")

        # Check if student_id already exists (if provided)
        if user_data.student_id:
            if await self.repository.student_id_exists(user_data.student_id):
                raise StudentIdAlreadyExistsError("Student ID already registered")

        # Hash password and create user
        password_hash = hash_password(user_data.password)
        entity = {
            "email": user_data.email,
            "password_hash": password_hash,
            "name": user_data.name,
            "student_id": user_data.student_id,
        }

        user = await self.repository.create(entity)
        logger.info(f"New user registered: {user_data.email}")
        return user

    async def login(self, credentials: UserLogin) -> Token:
        """Authenticate user and return JWT token."""
        user = await self.repository.get_by_email(credentials.email)

        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(credentials.password, user["password_hash"]):
            raise InvalidCredentialsError("Invalid email or password")

        if not user["is_active"]:
            raise AccountDeactivatedError("Account is deactivated")

        # Create access token
        token_data = {
            "sub": user["email"],
            "user_id": user["id"],
            "is_admin": user["is_admin"],
        }
        access_token = create_access_token(token_data)

        logger.info(f"User logged in: {credentials.email}")
        return Token(access_token=access_token)

    async def refresh_token(self, user_email: str) -> Token:
        """Refresh JWT token for authenticated user."""
        user = await self.repository.get_by_email(user_email)

        if not user or not user["is_active"]:
            raise UserNotFoundError("User not found or deactivated")

        # Create new access token
        token_data = {
            "sub": user["email"],
            "user_id": user["id"],
            "is_admin": user["is_admin"],
        }
        access_token = create_access_token(token_data)

        return Token(access_token=access_token)

    async def get_user_by_email(self, email: str) -> dict:
        """Get user by email."""
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundError("User not found")
        return user
