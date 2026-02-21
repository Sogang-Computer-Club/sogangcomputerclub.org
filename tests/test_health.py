import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint"""
    response = await client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data

    # Check services status (only database is checked now)
    services = data["services"]
    assert "database" in services
    assert services["database"] == "healthy"

    # Overall status should be healthy when database is up
    assert data["status"] == "healthy"
