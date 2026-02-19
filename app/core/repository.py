"""
Abstract repository pattern for data access.
Provides a consistent interface for data operations that can be easily mocked in tests.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')  # Entity type
ID = TypeVar('ID')  # ID type


class AbstractRepository(ABC, Generic[T, ID]):
    """
    Abstract base class for repository pattern.

    This provides a consistent interface for data operations that:
    1. Abstracts away database implementation details
    2. Makes testing easier with mock repositories
    3. Centralizes data access logic
    """

    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """Retrieve an entity by its ID."""
        ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Retrieve all entities with pagination."""
        ...

    @abstractmethod
    async def create(self, entity: dict) -> T:
        """Create a new entity."""
        ...

    @abstractmethod
    async def update(self, id: ID, data: dict) -> Optional[T]:
        """Update an existing entity."""
        ...

    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """Delete an entity by its ID. Returns True if deleted."""
        ...
