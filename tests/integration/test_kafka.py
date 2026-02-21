import pytest
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
import asyncio
import json


@pytest.mark.asyncio
async def test_kafka_producer_connection():
    """Test connection to Kafka producer"""
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        await producer.start()
        assert producer is not None

        await producer.stop()

    except Exception as e:
        pytest.fail(f"Failed to connect to Kafka producer: {e}")


@pytest.mark.asyncio
async def test_kafka_send_and_receive_message():
    """Test sending and receiving messages through Kafka"""
    topic_name = "test-topic"

    try:
        # Create producer
        producer = AIOKafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()

        # Create consumer
        consumer = AIOKafkaConsumer(
            topic_name,
            bootstrap_servers="localhost:9092",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="test-group",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await consumer.start()

        # Send a test message
        test_message = {
            "id": 1,
            "action": "test",
            "message": "Integration test message",
        }

        await producer.send_and_wait(topic_name, test_message)

        # Receive the message (with timeout)
        received = False

        async def consume_messages():
            nonlocal received
            async for msg in consumer:
                if msg.value == test_message:
                    received = True
                    break

        # Run consumer with timeout
        try:
            await asyncio.wait_for(consume_messages(), timeout=10.0)
        except asyncio.TimeoutError:
            pass

        assert received, "Failed to receive the test message"

        # Clean up
        await consumer.stop()
        await producer.stop()

    except Exception as e:
        pytest.fail(f"Failed to send and receive Kafka message: {e}")


@pytest.mark.asyncio
async def test_kafka_multiple_messages():
    """Test sending multiple messages to Kafka"""
    topic_name = "test-multiple-topic"

    try:
        producer = AIOKafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()

        # Send multiple messages
        messages = [{"id": i, "message": f"Test message {i}"} for i in range(5)]

        for msg in messages:
            await producer.send_and_wait(topic_name, msg)

        await producer.stop()

    except Exception as e:
        pytest.fail(f"Failed to send multiple Kafka messages: {e}")


@pytest.mark.asyncio
async def test_kafka_admin_client():
    """Test Kafka admin client connection"""
    try:
        admin_client = AIOKafkaAdminClient(bootstrap_servers="localhost:9092")

        await admin_client.start()
        assert admin_client is not None

        await admin_client.close()

    except Exception as e:
        pytest.fail(f"Failed to connect to Kafka admin client: {e}")


@pytest.mark.asyncio
async def test_kafka_topic_creation():
    """Test creating a Kafka topic"""
    topic_name = "test-creation-topic"

    try:
        admin_client = AIOKafkaAdminClient(bootstrap_servers="localhost:9092")

        await admin_client.start()

        # Create a new topic
        topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)

        try:
            await admin_client.create_topics([topic])
        except Exception as e:
            # Topic might already exist, which is fine
            if "already exists" not in str(e).lower():
                raise

        # List topics to verify creation
        topics = await admin_client.list_topics()
        assert topic_name in topics

        # Clean up - delete the test topic
        try:
            await admin_client.delete_topics([topic_name])
        except Exception:
            pass  # Ignore cleanup errors

        await admin_client.close()

    except Exception as e:
        pytest.fail(f"Failed to create Kafka topic: {e}")


@pytest.mark.asyncio
async def test_kafka_consumer_group():
    """Test Kafka consumer group functionality"""
    topic_name = "test-consumer-group-topic"
    group_id = "test-consumer-group"

    try:
        # Create producer
        producer = AIOKafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()

        # Send a message
        test_message = {"id": 1, "message": "Consumer group test"}
        await producer.send_and_wait(topic_name, test_message)

        # Create consumer with specific group
        consumer = AIOKafkaConsumer(
            topic_name,
            bootstrap_servers="localhost:9092",
            group_id=group_id,
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )
        await consumer.start()

        # Verify consumer can read the message
        received = False

        async def consume_messages():
            nonlocal received
            async for msg in consumer:
                if msg.value == test_message:
                    received = True
                    break

        try:
            await asyncio.wait_for(consume_messages(), timeout=10.0)
        except asyncio.TimeoutError:
            pass

        assert received, "Consumer failed to receive message"

        # Clean up
        await consumer.stop()
        await producer.stop()

    except Exception as e:
        pytest.fail(f"Failed to test Kafka consumer group: {e}")
