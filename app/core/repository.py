"""
리포지토리 패턴 추상화.

왜 리포지토리 패턴을 사용하는가:
1. 테스트 용이성: Mock 객체로 쉽게 교체 가능 (DB 없이 서비스 로직 테스트)
2. 관심사 분리: 비즈니스 로직(Service)과 데이터 접근(Repository) 분리
3. 데이터 소스 교체: PostgreSQL → MongoDB 등 변경 시 Repository만 수정
4. 트랜잭션 경계: Repository가 트랜잭션 단위를 명확히 정의

사용 시 주의:
- Service 계층에서는 항상 추상 인터페이스(AbstractRepository)에 의존
- 구체 구현체(MemoRepository)는 의존성 주입으로 제공
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")  # 엔티티 타입 (예: dict, Pydantic 모델)
ID = TypeVar("ID")  # 식별자 타입 (예: int, UUID)


class AbstractRepository(ABC, Generic[T, ID]):
    """
    리포지토리 패턴의 추상 기반 클래스.

    모든 도메인별 리포지토리는 이 클래스를 상속받아
    일관된 CRUD 인터페이스를 구현한다.
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
