"""
이벤트 발행 추상화 레이어.

비즈니스 로직을 메시지 브로커(Kafka, SQS)로부터 분리하여:
1. 테스트 시 NullEventPublisher로 교체 가능
2. 운영 환경에 따라 Kafka 또는 SQS 선택 가능
3. 서비스 코드 변경 없이 메시지 브로커 교체 가능

EVENT_BACKEND 환경변수로 구현체 선택:
- 'kafka': 로컬 개발용 (docker-compose에 포함)
- 'sqs': AWS 프로덕션용 (비용 절감, 관리형 서비스)
- 'null': 테스트용 (이벤트 발행 없이 기록만)
"""
from abc import ABC, abstractmethod
from aiokafka import AIOKafkaProducer
from ..core.config import get_settings
import json
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


class KafkaEventPublisher(AbstractEventPublisher):
    """Production event publisher using Kafka."""

    def __init__(self):
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Start the Kafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            logger.info("Kafka producer started successfully")
        except Exception as e:
            logger.warning(f"Failed to start Kafka producer: {e}")
            self.producer = None

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def publish(self, topic: str, message: dict) -> None:
        """Publish a message to a Kafka topic."""
        if self.producer:
            try:
                await self.producer.send_and_wait(topic, message)
            except Exception as e:
                logger.warning(f"Failed to publish to Kafka: {e}")

    @property
    def is_connected(self) -> bool:
        """Check if Kafka producer is connected."""
        return self.producer is not None


class SQSEventPublisher(AbstractEventPublisher):
    """
    AWS SQS event publisher.

    Uses aioboto3 for async SQS operations.
    Messages include the topic as a message attribute for routing.
    Reuses a single SQS client for efficiency.
    """

    def __init__(self):
        self._session = None
        self._client = None
        self._client_context = None
        self._queue_url = settings.sqs_queue_url

    async def start(self) -> None:
        """
        SQS 클라이언트 초기화.

        클라이언트를 한 번만 생성하여 모든 publish에서 재사용.
        매 요청마다 클라이언트를 생성하면 성능 저하 및 연결 누수 발생.
        """
        if not self._queue_url:
            logger.warning("SQS_QUEUE_URL not set, SQS publisher disabled")
            return

        try:
            import aioboto3
            self._session = aioboto3.Session()
            # 컨텍스트 매니저를 수동으로 진입하여 앱 수명 동안 클라이언트 유지
            self._client_context = self._session.client(
                'sqs',
                region_name=settings.aws_region
            )
            self._client = await self._client_context.__aenter__()
            logger.info(f"SQS publisher initialized for queue: {self._queue_url}")
        except ImportError:
            logger.error("aioboto3 not installed, SQS publisher disabled")
        except Exception as e:
            logger.warning(f"Failed to initialize SQS publisher: {e}")

    async def stop(self) -> None:
        """Cleanup SQS resources."""
        if self._client_context:
            try:
                await self._client_context.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing SQS client: {e}")
        self._client = None
        self._client_context = None
        self._session = None
        logger.info("SQS publisher stopped")

    async def publish(self, topic: str, message: dict, max_retries: int = 3) -> None:
        """
        SQS에 메시지 발행 (재시도 로직 포함).

        - topic은 MessageAttribute로 저장되어 SQS 필터링/라우팅에 사용
        - 일시적 실패(네트워크 오류 등) 시 지수 백오프로 재시도
        """
        if not self._client or not self._queue_url:
            return

        import asyncio
        last_error = None

        for attempt in range(max_retries):
            try:
                await self._client.send_message(
                    QueueUrl=self._queue_url,
                    MessageBody=json.dumps(message),
                    MessageAttributes={
                        'topic': {
                            'DataType': 'String',
                            'StringValue': topic
                        }
                    }
                )
                logger.debug(f"Published message to SQS topic={topic}")
                return  # 성공 시 즉시 반환
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # 지수 백오프: 0.5초 → 1초 → 2초 (일시적 장애 복구 대기)
                    wait_time = 0.5 * (2 ** attempt)
                    logger.warning(f"SQS publish failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)

        logger.error(f"Failed to publish to SQS after {max_retries} attempts: {last_error}")

    @property
    def is_connected(self) -> bool:
        """Check if SQS publisher is ready."""
        return self._client is not None and self._queue_url is not None


class NullEventPublisher(AbstractEventPublisher):
    """
    No-op event publisher for testing.

    Records published events for verification in tests.
    """

    def __init__(self):
        self.published_events: list[tuple[str, dict]] = []

    async def publish(self, topic: str, message: dict) -> None:
        """Record the event but don't actually publish."""
        self.published_events.append((topic, message))
        logger.debug(f"NullEventPublisher: recorded event to {topic}")

    @property
    def is_connected(self) -> bool:
        """Always returns True for testing."""
        return True

    def clear_events(self) -> None:
        """Clear recorded events (useful between tests)."""
        self.published_events.clear()


def create_event_publisher() -> AbstractEventPublisher:
    """
    Factory function to create the appropriate event publisher.

    Based on EVENT_BACKEND setting:
    - 'kafka': KafkaEventPublisher
    - 'sqs': SQSEventPublisher
    - 'null': NullEventPublisher
    """
    backend = settings.event_backend.lower()

    if backend == "sqs":
        logger.info("Using SQS event publisher")
        return SQSEventPublisher()
    elif backend == "kafka":
        logger.info("Using Kafka event publisher")
        return KafkaEventPublisher()
    else:
        logger.info("Using Null event publisher (no-op)")
        return NullEventPublisher()
