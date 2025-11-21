import pytest
import redis.asyncio as redis
import asyncio


@pytest.mark.asyncio
async def test_redis_connection():
    """Test connection to Redis"""
    try:
        redis_client = redis.from_url("redis://localhost:6380", decode_responses=True)
        pong = await redis_client.ping()

        assert pong is True

        await redis_client.aclose()

    except Exception as e:
        pytest.fail(f"Failed to connect to Redis: {e}")


@pytest.mark.asyncio
async def test_redis_set_and_get():
    """Test setting and getting values from Redis"""
    try:
        redis_client = redis.from_url("redis://localhost:6380", decode_responses=True)

        # Set a test value
        await redis_client.set("test_key", "test_value")

        # Get the value back
        value = await redis_client.get("test_key")

        assert value == "test_value"

        # Clean up - delete the test key
        await redis_client.delete("test_key")

        await redis_client.aclose()

    except Exception as e:
        pytest.fail(f"Failed to set and get Redis value: {e}")


@pytest.mark.asyncio
async def test_redis_expiration():
    """Test Redis key expiration"""
    try:
        redis_client = redis.from_url("redis://localhost:6380", decode_responses=True)

        # Set a key with 2 second expiration
        await redis_client.setex("expiring_key", 2, "expiring_value")

        # Verify it exists
        value = await redis_client.get("expiring_key")
        assert value == "expiring_value"

        # Wait for expiration
        await asyncio.sleep(3)

        # Verify it's gone
        value = await redis_client.get("expiring_key")
        assert value is None

        await redis_client.aclose()

    except Exception as e:
        pytest.fail(f"Failed to test Redis expiration: {e}")


@pytest.mark.asyncio
async def test_redis_delete():
    """Test deleting keys from Redis"""
    try:
        redis_client = redis.from_url("redis://localhost:6380", decode_responses=True)

        # Set multiple keys
        await redis_client.set("delete_test_1", "value1")
        await redis_client.set("delete_test_2", "value2")

        # Delete them
        deleted_count = await redis_client.delete("delete_test_1", "delete_test_2")

        assert deleted_count == 2

        # Verify they're gone
        value1 = await redis_client.get("delete_test_1")
        value2 = await redis_client.get("delete_test_2")

        assert value1 is None
        assert value2 is None

        await redis_client.aclose()

    except Exception as e:
        pytest.fail(f"Failed to test Redis delete: {e}")


@pytest.mark.asyncio
async def test_redis_exists():
    """Test checking if keys exist in Redis"""
    try:
        redis_client = redis.from_url("redis://localhost:6380", decode_responses=True)

        # Set a key
        await redis_client.set("exists_test", "value")

        # Check if it exists
        exists = await redis_client.exists("exists_test")
        assert exists == 1

        # Check for non-existent key
        not_exists = await redis_client.exists("nonexistent_key")
        assert not_exists == 0

        # Clean up
        await redis_client.delete("exists_test")

        await redis_client.aclose()

    except Exception as e:
        pytest.fail(f"Failed to test Redis exists: {e}")


@pytest.mark.asyncio
async def test_redis_json_data():
    """Test storing and retrieving JSON-like data in Redis"""
    try:
        import json

        redis_client = redis.from_url("redis://localhost:6380", decode_responses=True)

        # Store JSON data
        test_data = {
            "id": 1,
            "title": "Test Memo",
            "tags": ["test", "redis"]
        }

        await redis_client.set("json_test", json.dumps(test_data))

        # Retrieve and parse JSON data
        retrieved_data = await redis_client.get("json_test")
        parsed_data = json.loads(retrieved_data)

        assert parsed_data == test_data
        assert parsed_data["id"] == 1
        assert parsed_data["title"] == "Test Memo"
        assert parsed_data["tags"] == ["test", "redis"]

        # Clean up
        await redis_client.delete("json_test")

        await redis_client.aclose()

    except Exception as e:
        pytest.fail(f"Failed to test Redis JSON data: {e}")
