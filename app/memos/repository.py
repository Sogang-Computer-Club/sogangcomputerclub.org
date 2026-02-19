"""
Memo repository for data access.
Implements the repository pattern to abstract database operations.
"""
from abc import abstractmethod
from typing import Optional, List
import re
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.repository import AbstractRepository
from .models import memos


class AbstractMemoRepository(AbstractRepository[dict, int]):
    """Abstract interface for memo repository."""

    @abstractmethod
    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Search memos by keyword."""
        ...


class MemoRepository(AbstractMemoRepository):
    """SQLAlchemy implementation of the memo repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[dict]:
        """Retrieve a memo by its ID."""
        query = memos.select().where(memos.c.id == id)
        result = await self.session.execute(query)
        row = result.mappings().first()
        return dict(row) if row else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Retrieve all memos with pagination."""
        query = memos.select().order_by(memos.c.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [dict(row) for row in result.mappings().all()]

    async def create(self, entity: dict) -> dict:
        """Create a new memo."""
        query = memos.insert().values(**entity).returning(memos.c.id)
        result = await self.session.execute(query)
        created_id = result.scalar_one()
        await self.session.commit()

        # Fetch and return the created memo
        created_memo = await self.get_by_id(created_id)
        return created_memo  # type: ignore

    async def update(self, id: int, data: dict) -> Optional[dict]:
        """Update an existing memo."""
        query = memos.update().where(memos.c.id == id).values(**data)
        await self.session.execute(query)
        await self.session.commit()

        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        """Delete a memo by its ID."""
        query = memos.delete().where(memos.c.id == id)
        await self.session.execute(query)
        await self.session.commit()
        return True

    async def search(self, query: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """제목 또는 내용에서 키워드 검색."""
        # LIKE 패턴 특수문자(%, _, \) 이스케이프하여 패턴 인젝션 방지
        # 예: 사용자가 "100%"를 검색하면 "%100\%%" 로 변환되어 정확히 매칭
        escaped_q = re.sub(r'([%_\\])', r'\\\1', query)
        search_pattern = f"%{escaped_q}%"

        search_query = memos.select().where(
            sqlalchemy.or_(
                memos.c.title.like(search_pattern),
                memos.c.content.like(search_pattern)
            )
        ).order_by(memos.c.id.desc()).offset(skip).limit(limit)

        result = await self.session.execute(search_query)
        return [dict(row) for row in result.mappings().all()]
