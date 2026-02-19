"""
Unit tests for SQSEventPublisher.

Tests the SQS event publisher with mocked aioboto3 to avoid AWS dependencies.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


class TestSQSEventPublisher:
    """Tests for SQSEventPublisher class."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings with SQS configuration."""
        with patch('app.events.publisher.settings') as mock:
            mock.sqs_queue_url = "https://sqs.ap-northeast-2.amazonaws.com/123456789/test-queue"
            mock.aws_region = "ap-northeast-2"
            mock.event_backend = "sqs"
            mock.kafka_bootstrap_servers = "kafka:9092"
            yield mock

    @pytest.fixture
    def mock_aioboto3(self):
        """Mock aioboto3 session and client."""
        with patch('app.events.publisher.SQSEventPublisher._create_session') as mock_create:
            mock_session = MagicMock()
            mock_client = AsyncMock()
            mock_client_context = MagicMock()
            mock_client_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.client.return_value = mock_client_context
            mock_create.return_value = mock_session
            yield {
                'session': mock_session,
                'client': mock_client,
                'client_context': mock_client_context
            }

    @pytest.mark.asyncio
    async def test_sqs_publisher_init(self, mock_settings):
        """Test SQSEventPublisher initialization."""
        from app.events.publisher import SQSEventPublisher

        publisher = SQSEventPublisher()
        assert publisher._queue_url == mock_settings.sqs_queue_url
        assert publisher._client is None
        assert publisher._session is None

    @pytest.mark.asyncio
    async def test_sqs_publisher_start_without_queue_url(self):
        """Test that publisher is disabled when queue URL is not set."""
        with patch('app.events.publisher.settings') as mock_settings:
            mock_settings.sqs_queue_url = None
            mock_settings.aws_region = "ap-northeast-2"

            from app.events.publisher import SQSEventPublisher
            publisher = SQSEventPublisher()
            await publisher.start()

            assert not publisher.is_connected

    @pytest.mark.asyncio
    async def test_sqs_publisher_publish_when_not_connected(self, mock_settings):
        """Test that publish does nothing when not connected."""
        from app.events.publisher import SQSEventPublisher

        publisher = SQSEventPublisher()
        # Don't call start(), so publisher is not connected
        await publisher.publish("test-topic", {"key": "value"})
        # Should not raise, just return silently

    @pytest.mark.asyncio
    async def test_sqs_publisher_is_connected(self, mock_settings):
        """Test is_connected property."""
        from app.events.publisher import SQSEventPublisher

        publisher = SQSEventPublisher()
        assert not publisher.is_connected

        # Simulate connection
        publisher._client = MagicMock()
        assert publisher.is_connected

    @pytest.mark.asyncio
    async def test_create_event_publisher_sqs(self, mock_settings):
        """Test factory function creates SQS publisher when configured."""
        mock_settings.event_backend = "sqs"

        from app.events.publisher import create_event_publisher, SQSEventPublisher

        publisher = create_event_publisher()
        assert isinstance(publisher, SQSEventPublisher)

    @pytest.mark.asyncio
    async def test_create_event_publisher_kafka(self):
        """Test factory function creates Kafka publisher when configured."""
        with patch('app.events.publisher.settings') as mock_settings:
            mock_settings.event_backend = "kafka"
            mock_settings.kafka_bootstrap_servers = "kafka:9092"

            from app.events.publisher import create_event_publisher, KafkaEventPublisher

            publisher = create_event_publisher()
            assert isinstance(publisher, KafkaEventPublisher)

    @pytest.mark.asyncio
    async def test_create_event_publisher_null(self):
        """Test factory function creates Null publisher when configured."""
        with patch('app.events.publisher.settings') as mock_settings:
            mock_settings.event_backend = "null"

            from app.events.publisher import create_event_publisher, NullEventPublisher

            publisher = create_event_publisher()
            assert isinstance(publisher, NullEventPublisher)

    @pytest.mark.asyncio
    async def test_null_publisher_records_events(self):
        """Test NullEventPublisher records events for testing."""
        from app.events.publisher import NullEventPublisher

        publisher = NullEventPublisher()
        await publisher.publish("topic1", {"msg": "hello"})
        await publisher.publish("topic2", {"msg": "world"})

        assert len(publisher.published_events) == 2
        assert publisher.published_events[0] == ("topic1", {"msg": "hello"})
        assert publisher.published_events[1] == ("topic2", {"msg": "world"})

        publisher.clear_events()
        assert len(publisher.published_events) == 0

    @pytest.mark.asyncio
    async def test_null_publisher_always_connected(self):
        """Test NullEventPublisher is always connected."""
        from app.events.publisher import NullEventPublisher

        publisher = NullEventPublisher()
        assert publisher.is_connected is True
