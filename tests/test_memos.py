import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_memo(client: AsyncClient):
    """Test creating a new memo"""
    memo_data = {
        "title": "Test Memo",
        "content": "This is a test memo content",
        "tags": ["test", "pytest"],
        "priority": 3,
        "category": "testing",
        "is_archived": False,
        "is_favorite": True,
        "author": "Test User",
    }

    response = await client.post("/v1/memos/", json=memo_data)

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == memo_data["title"]
    assert data["content"] == memo_data["content"]
    assert data["tags"] == memo_data["tags"]
    assert data["priority"] == memo_data["priority"]
    assert data["category"] == memo_data["category"]
    assert data["is_archived"] == memo_data["is_archived"]
    assert data["is_favorite"] == memo_data["is_favorite"]
    assert data["author"] == "Test User"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_memo_minimal(client: AsyncClient):
    """Test creating a memo with minimal required fields"""
    memo_data = {"title": "Minimal Memo", "content": "Just the basics"}

    response = await client.post("/v1/memos/", json=memo_data)

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == memo_data["title"]
    assert data["content"] == memo_data["content"]
    assert data["tags"] == []
    assert data["priority"] == 2  # Default priority
    assert data["is_archived"] is False
    assert data["is_favorite"] is False


@pytest.mark.asyncio
async def test_create_memo_validation_error(client: AsyncClient):
    """Test creating a memo with invalid data"""
    # Missing required fields
    memo_data = {"title": "No content"}

    response = await client.post("/v1/memos/", json=memo_data)
    assert response.status_code == 422

    # Invalid priority
    memo_data = {
        "title": "Invalid Priority",
        "content": "Testing invalid priority",
        "priority": 10,  # Should be 1-4
    }

    response = await client.post("/v1/memos/", json=memo_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_memos(client: AsyncClient):
    """Test getting all memos"""
    # Create some test memos
    for i in range(3):
        memo_data = {"title": f"Test Memo {i}", "content": f"Content {i}"}
        await client.post("/v1/memos/", json=memo_data)

    # Get all memos
    response = await client.get("/v1/memos/")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3


@pytest.mark.asyncio
async def test_get_memos_with_pagination(client: AsyncClient):
    """Test getting memos with pagination"""
    # Create 10 test memos
    for i in range(10):
        memo_data = {"title": f"Memo {i}", "content": f"Content {i}"}
        await client.post("/v1/memos/", json=memo_data)

    # Get first 5 memos
    response = await client.get("/v1/memos/?skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

    # Get next 5 memos
    response = await client.get("/v1/memos/?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


@pytest.mark.asyncio
async def test_get_memo_by_id(client: AsyncClient):
    """Test getting a specific memo by ID"""
    # Create a memo
    memo_data = {"title": "Specific Memo", "content": "Specific content"}
    create_response = await client.post("/v1/memos/", json=memo_data)
    created_memo = create_response.json()

    # Get the memo by ID
    response = await client.get(f"/v1/memos/{created_memo['id']}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_memo["id"]
    assert data["title"] == memo_data["title"]
    assert data["content"] == memo_data["content"]


@pytest.mark.asyncio
async def test_get_memo_not_found(client: AsyncClient):
    """Test getting a memo that doesn't exist"""
    response = await client.get("/v1/memos/999999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_memo(client: AsyncClient):
    """Test updating a memo"""
    # Create a memo
    memo_data = {"title": "Original Title", "content": "Original content"}
    create_response = await client.post("/v1/memos/", json=memo_data)
    created_memo = create_response.json()

    # Update the memo
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "priority": 4,
        "is_favorite": True,
    }
    response = await client.put(f"/v1/memos/{created_memo['id']}", json=update_data)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == created_memo["id"]
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]
    assert data["priority"] == update_data["priority"]
    assert data["is_favorite"] == update_data["is_favorite"]


@pytest.mark.asyncio
async def test_update_memo_partial(client: AsyncClient):
    """Test partial update of a memo"""
    # Create a memo
    memo_data = {
        "title": "Original Title",
        "content": "Original content",
        "priority": 2,
    }
    create_response = await client.post("/v1/memos/", json=memo_data)
    created_memo = create_response.json()

    # Partial update (only title)
    update_data = {"title": "New Title Only"}
    response = await client.put(f"/v1/memos/{created_memo['id']}", json=update_data)

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["content"] == memo_data["content"]  # Should remain unchanged
    assert data["priority"] == memo_data["priority"]  # Should remain unchanged


@pytest.mark.asyncio
async def test_update_memo_not_found(client: AsyncClient):
    """Test updating a memo that doesn't exist"""
    update_data = {"title": "Updated Title"}
    response = await client.put("/v1/memos/999999", json=update_data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_memo_empty_data(client: AsyncClient):
    """Test updating a memo with no data"""
    # Create a memo
    memo_data = {"title": "Test Memo", "content": "Test content"}
    create_response = await client.post("/v1/memos/", json=memo_data)
    created_memo = create_response.json()

    # Try to update with empty data
    response = await client.put(f"/v1/memos/{created_memo['id']}", json={})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_memo(client: AsyncClient):
    """Test deleting a memo"""
    # Create a memo
    memo_data = {"title": "To Be Deleted", "content": "This will be deleted"}
    create_response = await client.post("/v1/memos/", json=memo_data)
    created_memo = create_response.json()

    # Delete the memo
    response = await client.delete(f"/v1/memos/{created_memo['id']}")

    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(f"/v1/memos/{created_memo['id']}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_memo_not_found(client: AsyncClient):
    """Test deleting a memo that doesn't exist"""
    response = await client.delete("/v1/memos/999999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_memos(client: AsyncClient):
    """Test searching memos by keyword"""
    # Create test memos
    memos_data = [
        {"title": "Python Tutorial", "content": "Learn Python programming"},
        {"title": "FastAPI Guide", "content": "Building APIs with FastAPI"},
        {"title": "Docker Basics", "content": "Introduction to Docker"},
    ]

    for memo_data in memos_data:
        await client.post("/v1/memos/", json=memo_data)

    # Search for "Python"
    response = await client.get("/v1/memos/search/?q=Python")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert "Python" in data[0]["title"]

    # Search for "API"
    response = await client.get("/v1/memos/search/?q=API")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert "API" in data[0]["content"]


@pytest.mark.asyncio
async def test_search_memos_no_results(client: AsyncClient):
    """Test searching with no matching results"""
    response = await client.get("/v1/memos/search/?q=nonexistent")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_search_memos_validation_error(client: AsyncClient):
    """Test search with invalid query parameter"""
    # Empty query should fail
    response = await client.get("/v1/memos/search/?q=")

    assert response.status_code == 422
