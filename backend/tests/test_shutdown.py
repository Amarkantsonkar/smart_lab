"""
Test cases for shutdown operations.
Tests shutdown validation, logging, and device state management.
"""

import pytest
from httpx import AsyncClient
from conftest import create_test_device, create_test_checklist_item, create_test_user

class TestShutdownValidation:
    """Test shutdown validation logic."""
    
    @pytest.mark.asyncio
    async def test_shutdown_blocked_when_critical_tasks_incomplete(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test that shutdown is blocked when critical tasks are incomplete."""
        # Create device and incomplete critical checklist item
        device = await create_test_device(clean_database, sample_device_data)
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": False}
        await create_test_checklist_item(clean_database, critical_item)
        
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        
        assert response.status_code == 400
        data = response.json()
        assert "checklist validation failed" in data["detail"]["message"].lower()
        assert "critical items incomplete" in data["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_shutdown_allowed_when_all_critical_tasks_complete(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test that shutdown is allowed when all critical tasks are complete."""
        # Create device and completed critical checklist item
        device = await create_test_device(clean_database, sample_device_data)
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": True}
        await create_test_checklist_item(clean_database, critical_item)
        
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["deviceId"] == device["deviceId"]
        assert "duration" in data
    
    @pytest.mark.asyncio
    async def test_shutdown_allowed_with_incomplete_non_critical_tasks(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test that shutdown is allowed even with incomplete non-critical tasks."""
        # Create device, completed critical item, and incomplete non-critical item
        device = await create_test_device(clean_database, sample_device_data)
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": True}
        non_critical_item = {"taskId": "NORMAL-001", "description": "Normal task", "category": "backup", "isCritical": False, "completed": False}
        
        await create_test_checklist_item(clean_database, critical_item)
        await create_test_checklist_item(clean_database, non_critical_item)
        
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    @pytest.mark.asyncio
    async def test_shutdown_device_not_found(self, async_client: AsyncClient, auth_headers_user):
        """Test shutdown attempt on non-existent device."""
        response = await async_client.post("/api/v1/shutdown/initiate/NONEXISTENT", headers=auth_headers_user)
        
        assert response.status_code == 404
        assert "device not found" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_shutdown_already_off_device(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test shutdown attempt on device that's already off."""
        # Create device that's already off
        off_device_data = {"deviceId": "OFF-001", "name": "Off Device", "status": "off", "type": "server", "location": "Rack A"}
        device = await create_test_device(clean_database, off_device_data)
        
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        
        assert response.status_code == 400
        assert "device is already off" in response.json()["detail"]["message"].lower()

class TestShutdownLogging:
    """Test shutdown logging functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_shutdown_logged(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data, sample_user_data):
        """Test that successful shutdown is properly logged."""
        # Create device and complete critical tasks
        device = await create_test_device(clean_database, sample_device_data)
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": True}
        await create_test_checklist_item(clean_database, critical_item)
        
        # Perform shutdown
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        assert response.status_code == 200
        
        # Check shutdown log was created
        logs_response = await async_client.get("/api/v1/shutdown-logs", headers=auth_headers_user)
        assert logs_response.status_code == 200
        
        logs = logs_response.json()
        assert len(logs) == 1
        log = logs[0]
        assert log["deviceId"] == device["deviceId"]
        assert log["status"] == "success"
        assert log["userName"] == sample_user_data["username"]
        assert "timestamp" in log
        assert "duration" in log
    
    @pytest.mark.asyncio
    async def test_failed_shutdown_logged(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data, sample_user_data):
        """Test that failed shutdown is properly logged."""
        # Create device with incomplete critical tasks
        device = await create_test_device(clean_database, sample_device_data)
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": False}
        await create_test_checklist_item(clean_database, critical_item)
        
        # Attempt shutdown (should fail)
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        assert response.status_code == 400
        
        # Check shutdown log was created
        logs_response = await async_client.get("/api/v1/shutdown-logs", headers=auth_headers_user)
        assert logs_response.status_code == 200
        
        logs = logs_response.json()
        assert len(logs) == 1
        log = logs[0]
        assert log["deviceId"] == device["deviceId"]
        assert log["status"] == "failed"
        assert log["userName"] == sample_user_data["username"]
        assert "errorMessage" in log
        assert "checklist validation failed" in log["errorMessage"].lower()
    
    @pytest.mark.asyncio
    async def test_shutdown_log_includes_checklist_validation(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test that shutdown log includes checklist validation details."""
        # Create device and mixed checklist items
        device = await create_test_device(clean_database, sample_device_data)
        critical_complete = {"taskId": "CRITICAL-001", "description": "Critical task 1", "category": "safety", "isCritical": True, "completed": True}
        critical_incomplete = {"taskId": "CRITICAL-002", "description": "Critical task 2", "category": "security", "isCritical": True, "completed": False}
        
        await create_test_checklist_item(clean_database, critical_complete)
        await create_test_checklist_item(clean_database, critical_incomplete)
        
        # Attempt shutdown
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        assert response.status_code == 400
        
        # Check log includes validation details
        logs_response = await async_client.get("/api/v1/shutdown-logs", headers=auth_headers_user)
        logs = logs_response.json()
        log = logs[0]
        
        assert "checklistValidation" in log
        validation = log["checklistValidation"]
        assert validation["allCompleted"] == False
        assert validation["criticalCompleted"] == False
        assert len(validation["incompleteItems"]) == 1
        assert validation["incompleteItems"][0] == "CRITICAL-002"

class TestShutdownDeviceStateUpdates:
    """Test device state updates during shutdown."""
    
    @pytest.mark.asyncio
    async def test_device_status_updated_on_successful_shutdown(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test that device status is updated to 'off' on successful shutdown."""
        # Create device and complete checklist
        device = await create_test_device(clean_database, sample_device_data)
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": True}
        await create_test_checklist_item(clean_database, critical_item)
        
        # Perform shutdown
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        assert response.status_code == 200
        
        # Check device status was updated
        device_response = await async_client.get(f"/api/v1/devices/{device['deviceId']}", headers=auth_headers_user)
        device_data = device_response.json()
        assert device_data["status"] == "off"
        assert "lastShutdown" in device_data
    
    @pytest.mark.asyncio
    async def test_device_status_unchanged_on_failed_shutdown(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_device_data):
        """Test that device status remains unchanged on failed shutdown."""
        # Create device with incomplete checklist
        device = await create_test_device(clean_database, sample_device_data)
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": False}
        await create_test_checklist_item(clean_database, critical_item)
        
        original_status = device["status"]
        
        # Attempt shutdown (should fail)
        response = await async_client.post(f"/api/v1/shutdown/initiate/{device['deviceId']}", headers=auth_headers_user)
        assert response.status_code == 400
        
        # Check device status was not changed
        device_response = await async_client.get(f"/api/v1/devices/{device['deviceId']}", headers=auth_headers_user)
        device_data = device_response.json()
        assert device_data["status"] == original_status
        assert device_data.get("lastShutdown") != device.get("lastShutdown")  # Should not be updated

class TestShutdownPermissions:
    """Test shutdown permission and authorization."""
    
    @pytest.mark.asyncio
    async def test_shutdown_without_authentication(self, async_client: AsyncClient, sample_device_data):
        """Test shutdown attempt without authentication fails."""
        response = await async_client.post("/api/v1/shutdown/initiate/DEVICE-001")
        
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_shutdown_with_invalid_token(self, async_client: AsyncClient, sample_device_data):
        """Test shutdown attempt with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.post("/api/v1/shutdown/initiate/DEVICE-001", headers=headers)
        
        assert response.status_code == 401
        assert "could not validate credentials" in response.json()["detail"]["message"].lower()

class TestShutdownAllDevices:
    """Test shutdown all devices functionality."""
    
    @pytest.mark.asyncio
    async def test_shutdown_all_devices_success(self, async_client: AsyncClient, auth_headers_admin, clean_database):
        """Test successful shutdown of all devices."""
        # Create multiple devices and complete checklist
        device1_data = {"deviceId": "DEV-001", "name": "Device 1", "status": "on", "type": "server", "location": "Rack A"}
        device2_data = {"deviceId": "DEV-002", "name": "Device 2", "status": "on", "type": "server", "location": "Rack B"}
        
        await create_test_device(clean_database, device1_data)
        await create_test_device(clean_database, device2_data)
        
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": True}
        await create_test_checklist_item(clean_database, critical_item)
        
        # Shutdown all devices
        response = await async_client.post("/api/v1/shutdown/initiate-all", headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["totalDevices"] == 2
        assert data["successfulShutdowns"] == 2
        assert data["failedShutdowns"] == 0
        assert data["allDevicesOff"] == True
    
    @pytest.mark.asyncio
    async def test_shutdown_all_devices_admin_only(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test that shutdown all devices requires admin privileges."""
        response = await async_client.post("/api/v1/shutdown/initiate-all", headers=auth_headers_user)
        
        assert response.status_code == 403
        assert "insufficient permissions" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_shutdown_all_devices_blocked_by_checklist(self, async_client: AsyncClient, auth_headers_admin, clean_database):
        """Test that shutdown all devices is blocked by incomplete checklist."""
        # Create devices with incomplete critical checklist
        device_data = {"deviceId": "DEV-001", "name": "Device 1", "status": "on", "type": "server", "location": "Rack A"}
        await create_test_device(clean_database, device_data)
        
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": False}
        await create_test_checklist_item(clean_database, critical_item)
        
        response = await async_client.post("/api/v1/shutdown/initiate-all", headers=auth_headers_admin)
        
        assert response.status_code == 400
        assert "checklist validation failed" in response.json()["detail"]["message"].lower()

class TestShutdownValidationEndpoint:
    """Test the dedicated checklist validation endpoint."""
    
    @pytest.mark.asyncio
    async def test_validate_checklist_endpoint(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test the checklist validation endpoint."""
        # Create mixed checklist items
        critical_complete = {"taskId": "CRITICAL-001", "description": "Critical complete", "category": "safety", "isCritical": True, "completed": True}
        critical_incomplete = {"taskId": "CRITICAL-002", "description": "Critical incomplete", "category": "security", "isCritical": True, "completed": False}
        normal_complete = {"taskId": "NORMAL-001", "description": "Normal complete", "category": "backup", "isCritical": False, "completed": True}
        
        await create_test_checklist_item(clean_database, critical_complete)
        await create_test_checklist_item(clean_database, critical_incomplete)
        await create_test_checklist_item(clean_database, normal_complete)
        
        response = await async_client.post("/api/v1/shutdown/validate-checklist", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["allCompleted"] == False
        assert data["criticalCompleted"] == False
        assert len(data["incompleteItems"]) == 1
        assert data["incompleteItems"][0]["taskId"] == "CRITICAL-002"
        assert data["totalItems"] == 3
        assert data["completedItems"] == 2
        assert data["criticalItems"] == 2
        assert data["completedCriticalItems"] == 1