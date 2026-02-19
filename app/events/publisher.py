"""
Event publisher abstraction for decoupling business logic from message brokers.

This module provides:
- AbstractEventPublisher: Interface for event publishing
- KafkaEventPublisher: Production implementation using aiokafka
- SQSEventPublisher: AWS SQS implementation using aioboto3
- NullEventPublisher: No-op implementation for testing

The event backend can be configured via EVENT_BACKEND environment variable:
- 'kafka': Use Kafka (default)
- 'sqs': Use AWS SQS
- 'null': Use NullEventPublisher (no-op)
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
        """Initialize the SQS client (reused for all publishes)."""
        if not self._queue_url:
            logger.warning("SQS_QUEUE_URL not set, SQS publisher disabled")
            return

        try:
            import aioboto3
            self._session = aioboto3.Session()
            # Create a persistent client context
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
        Publish a message to SQS with retry logic.

        The topic is included as a message attribute for routing/filtering.
        Implements exponential backoff for transient failures.
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
                return  # Success, exit retry loop
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Exponential backoff: 0.5s, 1s, 2s
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
