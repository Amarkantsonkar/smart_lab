"""
Test cases for device management endpoints.
Tests CRUD operations for devices with proper authentication and authorization.
"""

import pytest
from httpx import AsyncClient
from conftest import create_test_device, assert_device_response

class TestDeviceCreation:
    """Test device creation functionality."""
    
    @pytest.mark.asyncio
    async def test_create_device_success(self, async_client: AsyncClient, auth_headers_admin, sample_device_data):
        """Test successful device creation by admin."""
        response = await async_client.post("/api/v1/devices", json=sample_device_data, headers=auth_headers_admin)
        
        assert response.status_code == 201
        data = response.json()
        assert_device_response(data, sample_device_data)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_device_unauthorized(self, async_client: AsyncClient, auth_headers_user, sample_device_data):
        """Test device creation by non-admin user fails."""
        response = await async_client.post("/api/v1/devices", json=sample_device_data, headers=auth_headers_user)
        
        assert response.status_code == 403
        assert "insufficient permissions" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_create_device_duplicate_id(self, async_client: AsyncClient, auth_headers_admin, sample_device_data, clean_database):
        """Test creating device with duplicate deviceId fails."""
        # Create first device
        await async_client.post("/api/v1/devices", json=sample_device_data, headers=auth_headers_admin)
        
        # Try to create device with same deviceId
        duplicate_data = {**sample_device_data, "name": "Different Name"}
        response = await async_client.post("/api/v1/devices", json=duplicate_data, headers=auth_headers_admin)
        
        assert response.status_code == 400
        assert "device with this id already exists" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_create_device_invalid_data(self, async_client: AsyncClient, auth_headers_admin):
        """Test creating device with invalid data fails."""
        invalid_data = {
            "deviceId": "",  # Empty deviceId
            "name": "Test Device",
            "type": "invalid_type",  # Invalid type
            "status": "invalid_status"  # Invalid status
        }
        response = await async_client.post("/api/v1/devices", json=invalid_data, headers=auth_headers_admin)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_device_missing_required_fields(self, async_client: AsyncClient, auth_headers_admin):
        """Test creating device with missing required fields fails."""
        incomplete_data = {
            "name": "Test Device"
            # Missing deviceId and other required fields
        }
        response = await async_client.post("/api/v1/devices", json=incomplete_data, headers=auth_headers_admin)
        
        assert response.status_code == 422

class TestDeviceRetrieval:
    """Test device retrieval functionality."""
    
    @pytest.mark.asyncio
    async def test_get_all_devices(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test retrieving all devices."""
        # Create a test device first
        await create_test_device(clean_database, sample_device_data)
        
        response = await async_client.get("/api/v1/devices", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert_device_response(data[0], sample_device_data)
    
    @pytest.mark.asyncio
    async def test_get_device_by_id(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test retrieving device by ID."""
        # Create a test device first
        device = await create_test_device(clean_database, sample_device_data)
        
        response = await async_client.get(f"/api/v1/devices/{device['deviceId']}", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert_device_response(data, sample_device_data)
    
    @pytest.mark.asyncio
    async def test_get_device_not_found(self, async_client: AsyncClient, auth_headers_user):
        """Test retrieving non-existent device returns 404."""
        response = await async_client.get("/api/v1/devices/NONEXISTENT", headers=auth_headers_user)
        
        assert response.status_code == 404
        assert "device not found" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_get_devices_unauthorized(self, async_client: AsyncClient):
        """Test retrieving devices without authentication fails."""
        response = await async_client.get("/api/v1/devices")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_devices_empty_list(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test retrieving devices when none exist returns empty list."""
        response = await async_client.get("/api/v1/devices", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

class TestDeviceUpdates:
    """Test device update functionality."""
    
    @pytest.mark.asyncio
    async def test_update_device_success(self, async_client: AsyncClient, auth_headers_admin, clean_database, sample_device_data):
        """Test successful device update by admin."""
        # Create a test device first
        device = await create_test_device(clean_database, sample_device_data)
        
        update_data = {
            "name": "Updated Device Name",
            "status": "off",
            "location": "Updated Location"
        }
        
        response = await async_client.put(f"/api/v1/devices/{device['deviceId']}", json=update_data, headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["status"] == update_data["status"]
        assert data["location"] == update_data["location"]
        assert data["deviceId"] == device["deviceId"]  # Should not change
    
    @pytest.mark.asyncio
    async def test_update_device_unauthorized(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test device update by non-admin user fails."""
        # Create a test device first
        device = await create_test_device(clean_database, sample_device_data)
        
        update_data = {"name": "Updated Name"}
        response = await async_client.put(f"/api/v1/devices/{device['deviceId']}", json=update_data, headers=auth_headers_user)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_device_not_found(self, async_client: AsyncClient, auth_headers_admin):
        """Test updating non-existent device returns 404."""
        update_data = {"name": "Updated Name"}
        response = await async_client.put("/api/v1/devices/NONEXISTENT", json=update_data, headers=auth_headers_admin)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_device_invalid_data(self, async_client: AsyncClient, auth_headers_admin, clean_database, sample_device_data):
        """Test updating device with invalid data fails."""
        # Create a test device first
        device = await create_test_device(clean_database, sample_device_data)
        
        invalid_update = {
            "status": "invalid_status",
            "type": "invalid_type"
        }
        response = await async_client.put(f"/api/v1/devices/{device['deviceId']}", json=invalid_update, headers=auth_headers_admin)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_partial_update_device(self, async_client: AsyncClient, auth_headers_admin, clean_database, sample_device_data):
        """Test partial device update (PATCH)."""
        # Create a test device first
        device = await create_test_device(clean_database, sample_device_data)
        
        partial_update = {"status": "maintenance"}
        response = await async_client.patch(f"/api/v1/devices/{device['deviceId']}", json=partial_update, headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "maintenance"
        assert data["name"] == sample_device_data["name"]  # Other fields unchanged

class TestDeviceDeletion:
    """Test device deletion functionality."""
    
    @pytest.mark.asyncio
    async def test_delete_device_success(self, async_client: AsyncClient, auth_headers_admin, clean_database, sample_device_data):
        """Test successful device deletion by admin."""
        # Create a test device first
        device = await create_test_device(clean_database, sample_device_data)
        
        response = await async_client.delete(f"/api/v1/devices/{device['deviceId']}", headers=auth_headers_admin)
        
        assert response.status_code == 204
        
        # Verify device is deleted
        get_response = await async_client.get(f"/api/v1/devices/{device['deviceId']}", headers=auth_headers_admin)
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_device_unauthorized(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test device deletion by non-admin user fails."""
        # Create a test device first
        device = await create_test_device(clean_database, sample_device_data)
        
        response = await async_client.delete(f"/api/v1/devices/{device['deviceId']}", headers=auth_headers_user)
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_delete_device_not_found(self, async_client: AsyncClient, auth_headers_admin):
        """Test deleting non-existent device returns 404."""
        response = await async_client.delete("/api/v1/devices/NONEXISTENT", headers=auth_headers_admin)
        
        assert response.status_code == 404

class TestDeviceFiltering:
    """Test device filtering and search functionality."""
    
    @pytest.mark.asyncio
    async def test_filter_devices_by_status(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test filtering devices by status."""
        # Create devices with different statuses
        device1 = {"deviceId": "DEV-001", "name": "Device 1", "status": "on", "type": "server", "location": "Rack A"}
        device2 = {"deviceId": "DEV-002", "name": "Device 2", "status": "off", "type": "server", "location": "Rack B"}
        
        await create_test_device(clean_database, device1)
        await create_test_device(clean_database, device2)
        
        # Filter by status=on
        response = await async_client.get("/api/v1/devices?status=on", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "on"
    
    @pytest.mark.asyncio
    async def test_filter_devices_by_type(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test filtering devices by type."""
        # Create devices with different types
        device1 = {"deviceId": "DEV-001", "name": "Server 1", "status": "on", "type": "server", "location": "Rack A"}
        device2 = {"deviceId": "DEV-002", "name": "Switch 1", "status": "on", "type": "network", "location": "Rack B"}
        
        await create_test_device(clean_database, device1)
        await create_test_device(clean_database, device2)
        
        # Filter by type=server
        response = await async_client.get("/api/v1/devices?type=server", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "server"
    
    @pytest.mark.asyncio
    async def test_search_devices_by_name(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test searching devices by name."""
        # Create devices with different names
        device1 = {"deviceId": "DEV-001", "name": "Database Server", "status": "on", "type": "server", "location": "Rack A"}
        device2 = {"deviceId": "DEV-002", "name": "Web Server", "status": "on", "type": "server", "location": "Rack B"}
        
        await create_test_device(clean_database, device1)
        await create_test_device(clean_database, device2)
        
        # Search for "database"
        response = await async_client.get("/api/v1/devices?search=database", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "database" in data[0]["name"].lower()

class TestDeviceAssignment:
    """Test device assignment to users."""
    
    @pytest.mark.asyncio
    async def test_assign_device_to_user(self, async_client: AsyncClient, auth_headers_admin, clean_database, sample_device_data, sample_user_data):
        """Test assigning device to user."""
        # Create device and user
        device = await create_test_device(clean_database, sample_device_data)
        from conftest import create_test_user
        user = await create_test_user(clean_database, sample_user_data)
        
        assignment_data = {"userId": str(user["_id"])}
        response = await async_client.post(f"/api/v1/devices/{device['deviceId']}/assign", json=assignment_data, headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert str(user["_id"]) in data["assignedUsers"]
    
    @pytest.mark.asyncio
    async def test_unassign_device_from_user(self, async_client: AsyncClient, auth_headers_admin, clean_database, sample_device_data, sample_user_data):
        """Test unassigning device from user."""
        # Create device and user
        device = await create_test_device(clean_database, sample_device_data)
        from conftest import create_test_user
        user = await create_test_user(clean_database, sample_user_data)
        
        # First assign
        assignment_data = {"userId": str(user["_id"])}
        await async_client.post(f"/api/v1/devices/{device['deviceId']}/assign", json=assignment_data, headers=auth_headers_admin)
        
        # Then unassign
        response = await async_client.post(f"/api/v1/devices/{device['deviceId']}/unassign", json=assignment_data, headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert str(user["_id"]) not in data.get("assignedUsers", [])