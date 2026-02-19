"""
Event publisher abstraction for decoupling business logic from Kafka.

This module provides:
- AbstractEventPublisher: Interface for event publishing
- KafkaEventPublisher: Production implementation using aiokafka
- NullEventPublisher: No-op implementation for testing
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
