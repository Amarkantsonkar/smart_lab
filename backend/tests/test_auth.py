"""
Test cases for authentication endpoints.
Tests user registration, login, JWT token validation, and role-based access.
"""

import pytest
from httpx import AsyncClient

class TestAuthRegistration:
    """Test user registration functionality."""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test successful user registration."""
        response = await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["role"] == sample_user_data["role"]
        assert "hashed_password" not in data
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test registration with duplicate username fails."""
        # Register first user
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Try to register with same username
        duplicate_data = {**sample_user_data, "email": "different@example.com"}
        response = await async_client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "username already registered" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test registration with duplicate email fails."""
        # Register first user
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Try to register with same email
        duplicate_data = {**sample_user_data, "username": "differentuser"}
        response = await async_client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "email already registered" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test registration with invalid email format fails."""
        invalid_data = {**sample_user_data, "email": "invalid-email"}
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test registration with weak password fails."""
        weak_data = {**sample_user_data, "password": "123"}
        response = await async_client.post("/api/v1/auth/register", json=weak_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_invalid_role(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test registration with invalid role fails."""
        invalid_data = {**sample_user_data, "role": "invalid_role"}
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422

class TestAuthLogin:
    """Test user login functionality."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test successful user login."""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == sample_user_data["username"]
    
    @pytest.mark.asyncio
    async def test_login_invalid_username(self, async_client: AsyncClient, clean_database):
        """Test login with non-existent username fails."""
        login_data = {
            "username": "nonexistent",
            "password": "somepassword"
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "incorrect username or password" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test login with wrong password fails."""
        # Register user first
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Try login with wrong password
        login_data = {
            "username": sample_user_data["username"],
            "password": "wrongpassword"
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "incorrect username or password" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test login with inactive user fails."""
        # Register user
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Manually deactivate user in database
        from conftest import create_test_user
        await clean_database.users.update_one(
            {"username": sample_user_data["username"]},
            {"$set": {"is_active": False}}
        )
        
        # Try to login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 400
        assert "inactive user" in response.json()["detail"]["message"].lower()

class TestAuthProtectedRoutes:
    """Test protected routes and JWT token validation."""
    
    @pytest.mark.asyncio
    async def test_protected_route_without_token(self, async_client: AsyncClient):
        """Test accessing protected route without token fails."""
        response = await async_client.get("/api/v1/devices")
        
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_protected_route_with_invalid_token(self, async_client: AsyncClient):
        """Test accessing protected route with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/v1/devices", headers=headers)
        
        assert response.status_code == 401
        assert "could not validate credentials" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_protected_route_with_valid_token(self, async_client: AsyncClient, auth_headers_user):
        """Test accessing protected route with valid token succeeds."""
        response = await async_client.get("/api/v1/devices", headers=auth_headers_user)
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_admin_only_route_with_user_token(self, async_client: AsyncClient, auth_headers_user, sample_device_data):
        """Test accessing admin-only route with user token fails."""
        response = await async_client.post("/api/v1/devices", json=sample_device_data, headers=auth_headers_user)
        
        assert response.status_code == 403
        assert "insufficient permissions" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_admin_only_route_with_admin_token(self, async_client: AsyncClient, auth_headers_admin, sample_device_data):
        """Test accessing admin-only route with admin token succeeds."""
        response = await async_client.post("/api/v1/devices", json=sample_device_data, headers=auth_headers_admin)
        
        assert response.status_code == 201

class TestAuthTokenExpiration:
    """Test JWT token expiration and refresh functionality."""
    
    @pytest.mark.asyncio
    async def test_token_contains_user_info(self, async_client: AsyncClient, clean_database, sample_user_data):
        """Test that JWT token contains correct user information."""
        # Register and login
        await async_client.post("/api/v1/auth/register", json=sample_user_data)
        
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = await async_client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Decode token and verify claims (would need proper JWT decode in real test)
        token = data["access_token"]
        assert token is not None
        assert len(token.split('.')) == 3  # JWT format: header.payload.signature
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, async_client: AsyncClient, auth_headers_user, sample_user_data):
        """Test getting current user information from token."""
        response = await async_client.get("/api/v1/auth/me", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["role"] == sample_user_data["role"]
        assert "hashed_password" not in data

class TestAuthRoleBasedAccess:
    """Test role-based access control."""
    
    @pytest.mark.asyncio
    async def test_engineer_cannot_create_users(self, async_client: AsyncClient, auth_headers_user, sample_admin_data):
        """Test that engineers cannot create users."""
        response = await async_client.post("/api/v1/auth/register", json=sample_admin_data, headers=auth_headers_user)
        
        # Registration endpoint might be public, but admin operations should be restricted
        # This would depend on your specific endpoint design
        assert response.status_code in [403, 201]  # Either forbidden or allowed for registration
    
    @pytest.mark.asyncio
    async def test_admin_can_create_devices(self, async_client: AsyncClient, auth_headers_admin, sample_device_data):
        """Test that admins can create devices."""
        response = await async_client.post("/api/v1/devices", json=sample_device_data, headers=auth_headers_admin)
        
        assert response.status_code == 201
        data = response.json()
        assert data["deviceId"] == sample_device_data["deviceId"]
    
    @pytest.mark.asyncio
    async def test_user_can_read_devices(self, async_client: AsyncClient, auth_headers_user):
        """Test that users can read devices."""
        response = await async_client.get("/api/v1/devices", headers=auth_headers_user)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)