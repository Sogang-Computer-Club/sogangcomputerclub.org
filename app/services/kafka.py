"""
Kafka producer service for publishing events.
"""
from aiokafka import AIOKafkaProducer
from ..config import get_settings
import json
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class KafkaService:
    """Service for publishing messages to Kafka topics."""
    
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
    
    async def start(self):
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
    
    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def publish(self, topic: str, message: dict):
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


# Singleton instance
kafka_service = KafkaService()
