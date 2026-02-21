"""
User/Auth domain tests.
Tests for registration, login, token refresh, and user info endpoints.
"""

import pytest
from httpx import AsyncClient


# --- Registration Tests ---


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test successful user registration"""
    user_data = {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "name": "New User",
        "student_id": "20230001",
    }

    response = await client.post("/v1/auth/register", json=user_data)

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert data["student_id"] == user_data["student_id"]
    assert data["is_active"] is True
    assert data["is_admin"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    # Password should not be in response
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_user_minimal(client: AsyncClient):
    """Test user registration with minimal required fields"""
    user_data = {
        "email": "minimal@example.com",
        "password": "securepassword123",
        "name": "Minimal User",
        # student_id is optional
    }

    response = await client.post("/v1/auth/register", json=user_data)

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert data["student_id"] is None


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "securepassword123",
        "name": "First User",
    }

    # Register first user
    response = await client.post("/v1/auth/register", json=user_data)
    assert response.status_code == 201

    # Try to register with same email
    user_data["name"] = "Second User"
    response = await client.post("/v1/auth/register", json=user_data)

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_student_id(client: AsyncClient):
    """Test registration with duplicate student ID"""
    # Register first user with student_id
    user_data1 = {
        "email": "first@example.com",
        "password": "securepassword123",
        "name": "First User",
        "student_id": "20230001",
    }
    response = await client.post("/v1/auth/register", json=user_data1)
    assert response.status_code == 201

    # Try to register with same student_id but different email
    user_data2 = {
        "email": "second@example.com",
        "password": "securepassword123",
        "name": "Second User",
        "student_id": "20230001",
    }
    response = await client.post("/v1/auth/register", json=user_data2)

    assert response.status_code == 409
    assert "student id already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_validation_error(client: AsyncClient):
    """Test registration with invalid data"""
    # Missing required fields
    user_data = {"email": "incomplete@example.com"}
    response = await client.post("/v1/auth/register", json=user_data)
    assert response.status_code == 422

    # Invalid email format
    user_data = {
        "email": "not-an-email",
        "password": "securepassword123",
        "name": "Test User",
    }
    response = await client.post("/v1/auth/register", json=user_data)
    assert response.status_code == 422

    # Password too short
    user_data = {"email": "test@example.com", "password": "short", "name": "Test User"}
    response = await client.post("/v1/auth/register", json=user_data)
    assert response.status_code == 422


# --- Login Tests ---


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login"""
    # Register a user first
    user_data = {
        "email": "loginuser@example.com",
        "password": "securepassword123",
        "name": "Login User",
    }
    await client.post("/v1/auth/register", json=user_data)

    # Login
    login_data = {"email": "loginuser@example.com", "password": "securepassword123"}
    response = await client.post("/v1/auth/login", json=login_data)

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # Token should be a non-empty string
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    """Test login with non-existent email"""
    login_data = {"email": "nonexistent@example.com", "password": "securepassword123"}
    response = await client.post("/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    """Test login with wrong password"""
    # Register a user first
    user_data = {
        "email": "wrongpass@example.com",
        "password": "correctpassword123",
        "name": "Test User",
    }
    await client.post("/v1/auth/register", json=user_data)

    # Try to login with wrong password
    login_data = {"email": "wrongpass@example.com", "password": "wrongpassword123"}
    response = await client.post("/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_validation_error(client: AsyncClient):
    """Test login with invalid data"""
    # Missing password
    login_data = {"email": "test@example.com"}
    response = await client.post("/v1/auth/login", json=login_data)
    assert response.status_code == 422

    # Invalid email format
    login_data = {"email": "not-an-email", "password": "securepassword123"}
    response = await client.post("/v1/auth/login", json=login_data)
    assert response.status_code == 422


# --- Token Refresh Tests ---


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    """Test successful token refresh"""
    # Register and login
    user_data = {
        "email": "refresh@example.com",
        "password": "securepassword123",
        "name": "Refresh User",
    }
    await client.post("/v1/auth/register", json=user_data)

    login_response = await client.post(
        "/v1/auth/login",
        json={"email": "refresh@example.com", "password": "securepassword123"},
    )
    token = login_response.json()["access_token"]

    # Refresh token
    response = await client.post(
        "/v1/auth/refresh", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # New token should be different (due to different timestamp)
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_refresh_token_unauthorized(client: AsyncClient):
    """Test token refresh without authentication"""
    response = await client.post("/v1/auth/refresh")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """Test token refresh with invalid token"""
    response = await client.post(
        "/v1/auth/refresh", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


# --- Get Current User Tests ---


@pytest.mark.asyncio
async def test_get_current_user_success(client: AsyncClient):
    """Test getting current user info"""
    # Register and login
    user_data = {
        "email": "getme@example.com",
        "password": "securepassword123",
        "name": "Get Me User",
        "student_id": "20230099",
    }
    await client.post("/v1/auth/register", json=user_data)

    login_response = await client.post(
        "/v1/auth/login",
        json={"email": "getme@example.com", "password": "securepassword123"},
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = await client.get(
        "/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert data["student_id"] == user_data["student_id"]
    assert data["is_active"] is True
    assert "id" in data
    # Password should not be in response
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without authentication"""
    response = await client.get("/v1/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test getting current user with invalid token"""
    response = await client.get(
        "/v1/auth/me", headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401


# --- Integration Tests ---


@pytest.mark.asyncio
async def test_full_auth_flow(client: AsyncClient):
    """Test complete authentication flow: register -> login -> get me -> refresh"""
    # 1. Register
    user_data = {
        "email": "fullflow@example.com",
        "password": "securepassword123",
        "name": "Full Flow User",
    }
    register_response = await client.post("/v1/auth/register", json=user_data)
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # 2. Login
    login_response = await client.post(
        "/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Get current user
    me_response = await client.get(
        "/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["id"] == user_id

    # 4. Refresh token
    refresh_response = await client.post(
        "/v1/auth/refresh", headers={"Authorization": f"Bearer {token}"}
    )
    assert refresh_response.status_code == 200
    new_token = refresh_response.json()["access_token"]

    # 5. Use new token to get user
    me_response2 = await client.get(
        "/v1/auth/me", headers={"Authorization": f"Bearer {new_token}"}
    )
    assert me_response2.status_code == 200
    assert me_response2.json()["id"] == user_id


@pytest.mark.asyncio
async def test_registered_user_can_create_memo(client: AsyncClient):
    """Test that a registered user can create memos"""
    # Register and login
    user_data = {
        "email": "memouser@example.com",
        "password": "securepassword123",
        "name": "Memo User",
    }
    await client.post("/v1/auth/register", json=user_data)

    login_response = await client.post(
        "/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    token = login_response.json()["access_token"]

    # Create a memo
    memo_data = {"title": "User's Memo", "content": "Created by registered user"}
    response = await client.post(
        "/v1/memos/", json=memo_data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == memo_data["title"]
    # Author should be set to user's email
    assert data["author"] == user_data["email"]
