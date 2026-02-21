"""
Memo service containing business logic.
Orchestrates repository and event publisher.
"""

from typing import List
import logging

from .repository import AbstractMemoRepository
from .schemas import MemoCreate, MemoUpdate
from ..events.publisher import AbstractEventPublisher
from ..common.metrics import MEMO_COUNT

logger = logging.getLogger(__name__)


class MemoNotFoundError(Exception):
    """Raised when a memo is not found."""

    pass


class MemoForbiddenError(Exception):
    """Raised when user is not authorized to modify a memo."""

    pass


class MemoService:
    """Service layer for memo operations."""

    def __init__(
        self,
        repository: AbstractMemoRepository,
        event_publisher: AbstractEventPublisher,
    ):
        self.repository = repository
        self.event_publisher = event_publisher

    def _check_ownership(self, memo: dict, current_user: dict) -> bool:
        """Check if current user owns the memo or is admin."""
        if current_user.get("is_admin", False):
            return True
        user_email = current_user.get("sub", "")
        return memo.get("author") == user_email

    async def create_memo(self, memo: MemoCreate, user_email: str) -> dict:
        """Create a new memo."""
        entity = {
            "title": memo.title,
            "content": memo.content,
            "tags": memo.tags or [],
            "priority": memo.priority,
            "category": memo.category,
            "is_archived": memo.is_archived,
            "is_favorite": memo.is_favorite,
            "author": user_email,
        }

        created_memo = await self.repository.create(entity)

        # Publish event
        await self.event_publisher.publish(
            "memo-created",
            {"id": created_memo["id"], "title": memo.title, "action": "created"},
        )

        MEMO_COUNT.inc()
        return created_memo

    async def get_memos(self, skip: int = 0, limit: int = 100) -> List[dict]:
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
    ) -> List[dict]:
        """Search memos by keyword."""
        return await self.repository.search(query, skip, limit)

    async def update_memo(
        self, memo_id: int, memo_update: MemoUpdate, current_user: dict
    ) -> dict:
        """Update a memo."""
        existing_memo = await self.repository.get_by_id(memo_id)
        if existing_memo is None:
            raise MemoNotFoundError(f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        if not self._check_ownership(existing_memo, current_user):
            raise MemoForbiddenError("Not authorized to modify this memo")

        update_data = memo_update.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("수정할 내용이 없습니다.")

        updated_memo = await self.repository.update(memo_id, update_data)

        # Publish event
        await self.event_publisher.publish(
            "memo-updated", {"id": memo_id, "action": "updated"}
        )

        return updated_memo  # type: ignore

    async def delete_memo(self, memo_id: int, current_user: dict) -> None:
        """Delete a memo."""
        existing_memo = await self.repository.get_by_id(memo_id)
        if existing_memo is None:
            raise MemoNotFoundError(f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        if not self._check_ownership(existing_memo, current_user):
            raise MemoForbiddenError("Not authorized to delete this memo")

        await self.repository.delete(memo_id)

        # Publish event
        await self.event_publisher.publish(
            "memo-deleted", {"id": memo_id, "action": "deleted"}
        )

        MEMO_COUNT.dec()
