"""
User repository for data access.
Implements the repository pattern to abstract database operations.
"""
from abc import abstractmethod
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.repository import AbstractRepository
from .models import users


class AbstractUserRepository(AbstractRepository[dict, int]):
    """Abstract interface for user repository."""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[dict]:
        """Retrieve a user by email address."""
        ...

    @abstractmethod
    async def get_by_student_id(self, student_id: str) -> Optional[dict]:
        """Retrieve a user by student ID."""
        ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        ...

    @abstractmethod
    async def student_id_exists(self, student_id: str) -> bool:
        """Check if student ID already exists."""
        ...


class UserRepository(AbstractUserRepository):
    """SQLAlchemy implementation of the user repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[dict]:
        """Retrieve a user by ID."""
        query = select(users).where(users.c.id == id)
        result = await self.session.execute(query)
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Retrieve all users with pagination."""
        query = select(users).order_by(users.c.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [dict(row) for row in result.mappings().all()]

    async def create(self, entity: dict) -> dict:
        """Create a new user."""
        query = users.insert().values(**entity).returning(users.c.id)
        result = await self.session.execute(query)
        user_id = result.scalar_one()
        await self.session.commit()

        # Fetch and return the created user
        created_user = await self.get_by_id(user_id)
        if created_user is None:
            raise RuntimeError(f"Failed to fetch created user with id {user_id}")
        return created_user

    async def update(self, id: int, data: dict) -> Optional[dict]:
        """Update an existing user."""
        query = users.update().where(users.c.id == id).values(**data)
        await self.session.execute(query)
        await self.session.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        """Delete a user by ID."""
        query = users.delete().where(users.c.id == id)
        await self.session.execute(query)
        await self.session.commit()
        return True

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Retrieve a user by email address."""
        query = select(users).where(users.c.email == email)
        result = await self.session.execute(query)
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_by_student_id(self, student_id: str) -> Optional[dict]:
        """Retrieve a user by student ID."""
        query = select(users).where(users.c.student_id == student_id)
        result = await self.session.execute(query)
        row = result.mappings().first()
        return dict(row) if row else None

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        existing = await self.get_by_email(email)
        return existing is not None

    async def student_id_exists(self, student_id: str) -> bool:
        """Check if student ID already exists."""
        existing = await self.get_by_student_id(student_id)
        return existing is not None
