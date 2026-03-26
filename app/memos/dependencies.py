"""
Memo domain dependency injection.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_db
from ..events.dependencies import get_event_publisher
from ..events.publisher import NullEventPublisher
from .repository import MemoRepository, AbstractMemoRepository
from .service import MemoService


async def get_memo_repository(
    db: AsyncSession = Depends(get_db),
) -> AbstractMemoRepository:
    """Dependency that provides the memo repository."""
    return MemoRepository(db)


async def get_memo_service(
    repository: AbstractMemoRepository = Depends(get_memo_repository),
    event_publisher: NullEventPublisher = Depends(get_event_publisher),
) -> MemoService:
    """Dependency that provides the memo service."""
    return MemoService(repository, event_publisher)
