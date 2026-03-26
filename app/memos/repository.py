"""
Memo repository for data access.
Implements the repository pattern to abstract database operations.
"""

from abc import abstractmethod
import re
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.repository import AbstractRepository
from .models import memos


class AbstractMemoRepository(AbstractRepository[dict, int]):
    """Abstract interface for memo repository."""

    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> list[dict]:
        """Search memos by keyword."""
        ...


class MemoRepository(AbstractMemoRepository):
    """SQLAlchemy implementation of the memo repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> dict | None:
        """Retrieve a memo by its ID."""
        query = memos.select().where(memos.c.id == id)
        result = await self.session.execute(query)
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """Retrieve all memos with pagination."""
        query = memos.select().order_by(memos.c.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [dict(row) for row in result.mappings().all()]

    async def create(self, entity: dict) -> dict:
        """Create a new memo. Returns the created memo."""
        query = memos.insert().values(**entity).returning(*memos.c)
        result = await self.session.execute(query)
        await self.session.commit()
        row = result.mappings().one()
        return dict(row)

    async def update(self, id: int, data: dict) -> dict | None:
        """Update an existing memo. Returns the updated memo or None if not found."""
        query = (
            memos.update().where(memos.c.id == id).values(**data).returning(*memos.c)
        )
        result = await self.session.execute(query)
        await self.session.commit()
        row = result.mappings().first()
        return dict(row) if row else None

    async def delete(self, id: int) -> bool:
        """Delete a memo by its ID. Returns True if deleted, False if not found."""
        query = memos.delete().where(memos.c.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def search(self, query: str, skip: int = 0, limit: int = 100) -> list[dict]:
        """제목 또는 내용에서 키워드 검색."""
        # LIKE 패턴 특수문자(%, _, \) 이스케이프하여 패턴 인젝션 방지
        escaped_q = re.sub(r"([%_\\])", r"\\\1", query)
        search_pattern = f"%{escaped_q}%"

        search_query = (
            memos.select()
            .where(
                sqlalchemy.or_(
                    memos.c.title.like(search_pattern),
                    memos.c.content.like(search_pattern),
                )
            )
            .order_by(memos.c.id.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(search_query)
        return [dict(row) for row in result.mappings().all()]
