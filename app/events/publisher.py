"""
이벤트 발행 추상화 레이어.

비즈니스 로직을 메시지 브로커(Kafka, SQS)로부터 분리하여:
1. 테스트 시 NullEventPublisher로 교체 가능
2. 운영 환경에 따라 Kafka 또는 SQS 선택 가능
3. 서비스 코드 변경 없이 메시지 브로커 교체 가능

EVENT_BACKEND 환경변수로 구현체 선택:
- 'null': 기본값 (동아리 규모에서 이벤트 시스템 불필요)
- 'kafka': 로컬 개발용 (aiokafka 설치 필요)
- 'sqs': AWS 프로덕션용 (boto3, aioboto3 설치 필요)

Note: 동아리 프로젝트 규모에서 Kafka/SQS는 과도하여 기본 비활성화됨.
필요 시 pyproject.toml에 의존성 추가 후 활성화 가능.
"""

from abc import ABC, abstractmethod
from ..core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class AbstractEventPublisher(ABC):
    """
    Abstract base class for event publishing.

    This abstraction allows:
    1. Easy testing with NullEventPublisher
    2. Swapping Kafka for another message broker
    3. Adding decorators/wrappers around publishing
    """

    @abstractmethod
    async def publish(self, topic: str, message: dict) -> None:
        """Publish a message to a topic."""
        ...

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the publisher is connected."""
        ...

    async def start(self) -> None:
        """Start the publisher (optional for implementations)."""
        pass

    async def stop(self) -> None:
        """Stop the publisher (optional for implementations)."""
        pass


class NullEventPublisher(AbstractEventPublisher):
    """
    No-op event publisher (기본값).

    이벤트를 로깅만 하고 실제 발행하지 않음.
    동아리 규모에서는 이벤트 시스템이 불필요하여 기본값으로 설정.
    테스트에서도 사용 가능.
    """

    def __init__(self):
        self.published_events: list[tuple[str, dict]] = []

    async def publish(self, topic: str, message: dict) -> None:
        """Record the event but don't actually publish."""
        self.published_events.append((topic, message))
        logger.debug(f"NullEventPublisher: recorded event to {topic}")

    @property
    def is_connected(self) -> bool:
        """Always returns True."""
        return True

    def clear_events(self) -> None:
        """Clear recorded events (useful between tests)."""
        self.published_events.clear()


def create_event_publisher() -> AbstractEventPublisher:
    """
    Factory function to create the appropriate event publisher.

    Based on EVENT_BACKEND setting:
    - 'null': NullEventPublisher (기본값)
    - 'kafka': KafkaEventPublisher (aiokafka 설치 필요)
    - 'sqs': SQSEventPublisher (boto3, aioboto3 설치 필요)
    """
    backend = settings.event_backend.lower()

    if backend == "sqs":
        try:
            from .publisher_sqs import SQSEventPublisher

            logger.info("Using SQS event publisher")
            return SQSEventPublisher()
        except ImportError:
            logger.warning(
                "SQS backend requested but aioboto3 not installed. Falling back to NullEventPublisher."
            )
            return NullEventPublisher()

    elif backend == "kafka":
        try:
            from .publisher_kafka import KafkaEventPublisher

            logger.info("Using Kafka event publisher")
            return KafkaEventPublisher()
        except ImportError:
            logger.warning(
                "Kafka backend requested but aiokafka not installed. Falling back to NullEventPublisher."
            )
            return NullEventPublisher()

    else:
        logger.info("Using Null event publisher (no-op, 기본값)")
        return NullEventPublisher()
