"""
Memo service containing business logic.
Orchestrates repository and event publisher.
"""

import logging

from .repository import AbstractMemoRepository
from .schemas import MemoCreate, MemoUpdate
from ..events.publisher import NullEventPublisher
from ..common.metrics import MEMO_COUNT

logger = logging.getLogger(__name__)


class MemoNotFoundError(Exception):
    """Raised when a memo is not found."""

    pass


class MemoService:
    """Service layer for memo operations."""

    def __init__(
        self,
        repository: AbstractMemoRepository,
        event_publisher: NullEventPublisher,
    ):
        self.repository = repository
        self.event_publisher = event_publisher

    async def create_memo(self, memo: MemoCreate, author: str) -> dict:
        """Create a new memo."""
        entity = {
            "title": memo.title,
            "content": memo.content,
            "tags": memo.tags or [],
            "priority": memo.priority,
            "category": memo.category,
            "is_archived": memo.is_archived,
            "is_favorite": memo.is_favorite,
            "author": author,
        }

        created_memo = await self.repository.create(entity)

        # Publish event
        await self.event_publisher.publish(
            "memo-created",
            {"id": created_memo["id"], "title": memo.title, "action": "created"},
        )

        MEMO_COUNT.inc()
        return created_memo

    async def get_memos(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get all memos with pagination."""
        return await self.repository.get_all(skip, limit)

    async def get_memo(self, memo_id: int) -> dict:
        """Get a specific memo by ID."""
        memo = await self.repository.get_by_id(memo_id)
        if memo is None:
            raise MemoNotFoundError(f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")
        return memo

    async def search_memos(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        """Search memos by keyword."""
        return await self.repository.search(query, skip, limit)

    async def update_memo(self, memo_id: int, memo_update: MemoUpdate) -> dict:
        """Update a memo atomically (no TOCTOU race)."""
        update_data = memo_update.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("수정할 내용이 없습니다.")

        updated_memo = await self.repository.update(memo_id, update_data)
        if updated_memo is None:
            raise MemoNotFoundError(f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        await self.event_publisher.publish(
            "memo-updated", {"id": memo_id, "action": "updated"}
        )

        return updated_memo

    async def delete_memo(self, memo_id: int) -> None:
        """Delete a memo atomically (no TOCTOU race)."""
        deleted = await self.repository.delete(memo_id)
        if not deleted:
            raise MemoNotFoundError(f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        await self.event_publisher.publish(
            "memo-deleted", {"id": memo_id, "action": "deleted"}
        )

        MEMO_COUNT.dec()
