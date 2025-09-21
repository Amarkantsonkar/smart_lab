"""
Test cases for checklist management endpoints.
Tests CRUD operations for checklist items and completion tracking.
"""

import pytest
from httpx import AsyncClient
from conftest import create_test_checklist_item, assert_checklist_response

class TestChecklistCreation:
    """Test checklist item creation functionality."""
    
    @pytest.mark.asyncio
    async def test_create_checklist_item_success(self, async_client: AsyncClient, auth_headers_admin, sample_checklist_data):
        """Test successful checklist item creation by admin."""
        response = await async_client.post("/api/v1/checklist", json=sample_checklist_data, headers=auth_headers_admin)
        
        assert response.status_code == 201
        data = response.json()
        assert_checklist_response(data, sample_checklist_data)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_checklist_item_unauthorized(self, async_client: AsyncClient, auth_headers_user, sample_checklist_data):
        """Test checklist item creation by non-admin user fails."""
        response = await async_client.post("/api/v1/checklist", json=sample_checklist_data, headers=auth_headers_user)
        
        assert response.status_code == 403
        assert "insufficient permissions" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_create_checklist_item_duplicate_id(self, async_client: AsyncClient, auth_headers_admin, sample_checklist_data, clean_database):
        """Test creating checklist item with duplicate taskId fails."""
        # Create first item
        await async_client.post("/api/v1/checklist", json=sample_checklist_data, headers=auth_headers_admin)
        
        # Try to create item with same taskId
        duplicate_data = {**sample_checklist_data, "description": "Different Description"}
        response = await async_client.post("/api/v1/checklist", json=duplicate_data, headers=auth_headers_admin)
        
        assert response.status_code == 400
        assert "task with this id already exists" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_create_checklist_item_invalid_category(self, async_client: AsyncClient, auth_headers_admin, sample_checklist_data):
        """Test creating checklist item with invalid category fails."""
        invalid_data = {**sample_checklist_data, "category": "invalid_category"}
        response = await async_client.post("/api/v1/checklist", json=invalid_data, headers=auth_headers_admin)
        
        assert response.status_code == 422

class TestChecklistRetrieval:
    """Test checklist retrieval functionality."""
    
    @pytest.mark.asyncio
    async def test_get_all_checklist_items(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_checklist_data):
        """Test retrieving all checklist items."""
        # Create a test checklist item first
        await create_test_checklist_item(clean_database, sample_checklist_data)
        
        response = await async_client.get("/api/v1/checklist", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert_checklist_response(data[0], sample_checklist_data)
    
    @pytest.mark.asyncio
    async def test_get_checklist_item_by_id(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_checklist_data):
        """Test retrieving checklist item by ID."""
        # Create a test checklist item first
        item = await create_test_checklist_item(clean_database, sample_checklist_data)
        
        response = await async_client.get(f"/api/v1/checklist/{item['taskId']}", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert_checklist_response(data, sample_checklist_data)
    
    @pytest.mark.asyncio
    async def test_get_checklist_item_not_found(self, async_client: AsyncClient, auth_headers_user):
        """Test retrieving non-existent checklist item returns 404."""
        response = await async_client.get("/api/v1/checklist/NONEXISTENT", headers=auth_headers_user)
        
        assert response.status_code == 404
        assert "task not found" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_filter_checklist_by_category(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test filtering checklist items by category."""
        # Create items with different categories
        safety_item = {"taskId": "SAFETY-001", "description": "Safety task", "category": "safety", "isCritical": True, "completed": False}
        security_item = {"taskId": "SECURITY-001", "description": "Security task", "category": "security", "isCritical": True, "completed": False}
        
        await create_test_checklist_item(clean_database, safety_item)
        await create_test_checklist_item(clean_database, security_item)
        
        # Filter by category=safety
        response = await async_client.get("/api/v1/checklist?category=safety", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "safety"
    
    @pytest.mark.asyncio
    async def test_filter_checklist_by_criticality(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test filtering checklist items by criticality."""
        # Create critical and non-critical items
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": False}
        non_critical_item = {"taskId": "NORMAL-001", "description": "Normal task", "category": "backup", "isCritical": False, "completed": False}
        
        await create_test_checklist_item(clean_database, critical_item)
        await create_test_checklist_item(clean_database, non_critical_item)
        
        # Filter by critical=true
        response = await async_client.get("/api/v1/checklist?critical=true", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["isCritical"] == True
    
    @pytest.mark.asyncio
    async def test_filter_checklist_by_completion_status(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test filtering checklist items by completion status."""
        # Create completed and pending items
        completed_item = {"taskId": "COMPLETED-001", "description": "Completed task", "category": "safety", "isCritical": True, "completed": True}
        pending_item = {"taskId": "PENDING-001", "description": "Pending task", "category": "safety", "isCritical": True, "completed": False}
        
        await create_test_checklist_item(clean_database, completed_item)
        await create_test_checklist_item(clean_database, pending_item)
        
        # Filter by completed=false
        response = await async_client.get("/api/v1/checklist?completed=false", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["completed"] == False

class TestChecklistCompletion:
    """Test checklist item completion functionality."""
    
    @pytest.mark.asyncio
    async def test_mark_checklist_item_complete(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_checklist_data, sample_user_data):
        """Test marking checklist item as complete."""
        # Create a test checklist item
        item = await create_test_checklist_item(clean_database, sample_checklist_data)
        
        completion_data = {"completed": True}
        response = await async_client.put(f"/api/v1/checklist/{item['taskId']}", json=completion_data, headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == True
        assert "completedBy" in data
        assert "completedAt" in data
    
    @pytest.mark.asyncio
    async def test_mark_checklist_item_incomplete(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test marking checklist item as incomplete."""
        # Create a completed checklist item
        completed_item = {"taskId": "COMPLETED-001", "description": "Completed task", "category": "safety", "isCritical": True, "completed": True}
        item = await create_test_checklist_item(clean_database, completed_item)
        
        completion_data = {"completed": False}
        response = await async_client.put(f"/api/v1/checklist/{item['taskId']}", json=completion_data, headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == False
        assert data.get("completedBy") is None
        assert data.get("completedAt") is None
    
    @pytest.mark.asyncio
    async def test_completion_tracks_user(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_checklist_data, sample_user_data):
        """Test that completion tracking includes user information."""
        # Create a test checklist item
        item = await create_test_checklist_item(clean_database, sample_checklist_data)
        
        completion_data = {"completed": True}
        response = await async_client.put(f"/api/v1/checklist/{item['taskId']}", json=completion_data, headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == True
        assert data["completedBy"] == sample_user_data["username"]
        assert data["completedAt"] is not None

class TestChecklistValidation:
    """Test checklist validation logic for shutdown operations."""
    
    @pytest.mark.asyncio
    async def test_validate_checklist_all_critical_complete(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test checklist validation when all critical items are complete."""
        # Create critical items - all completed
        critical_item1 = {"taskId": "CRITICAL-001", "description": "Critical task 1", "category": "safety", "isCritical": True, "completed": True}
        critical_item2 = {"taskId": "CRITICAL-002", "description": "Critical task 2", "category": "security", "isCritical": True, "completed": True}
        non_critical_item = {"taskId": "NORMAL-001", "description": "Normal task", "category": "backup", "isCritical": False, "completed": False}
        
        await create_test_checklist_item(clean_database, critical_item1)
        await create_test_checklist_item(clean_database, critical_item2)
        await create_test_checklist_item(clean_database, non_critical_item)
        
        response = await async_client.post("/api/v1/shutdown/validate-checklist", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["allCompleted"] == True
        assert data["criticalCompleted"] == True
        assert len(data["incompleteItems"]) == 0
    
    @pytest.mark.asyncio
    async def test_validate_checklist_critical_incomplete(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test checklist validation when critical items are incomplete."""
        # Create critical items - some incomplete
        critical_item1 = {"taskId": "CRITICAL-001", "description": "Critical task 1", "category": "safety", "isCritical": True, "completed": True}
        critical_item2 = {"taskId": "CRITICAL-002", "description": "Critical task 2", "category": "security", "isCritical": True, "completed": False}
        
        await create_test_checklist_item(clean_database, critical_item1)
        await create_test_checklist_item(clean_database, critical_item2)
        
        response = await async_client.post("/api/v1/shutdown/validate-checklist", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["allCompleted"] == False
        assert data["criticalCompleted"] == False
        assert len(data["incompleteItems"]) == 1
        assert data["incompleteItems"][0]["taskId"] == "CRITICAL-002"
    
    @pytest.mark.asyncio
    async def test_validate_empty_checklist(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test checklist validation when no items exist."""
        response = await async_client.post("/api/v1/shutdown/validate-checklist", headers=auth_headers_user)
        
        assert response.status_code == 200
        data = response.json()
        assert data["allCompleted"] == True
        assert data["criticalCompleted"] == True
        assert len(data["incompleteItems"]) == 0

class TestChecklistUpdates:
    """Test checklist item update functionality."""
    
    @pytest.mark.asyncio
    async def test_update_checklist_item_description(self, async_client: AsyncClient, auth_headers_admin, clean_database, sample_checklist_data):
        """Test updating checklist item description."""
        # Create a test checklist item
        item = await create_test_checklist_item(clean_database, sample_checklist_data)
        
        update_data = {"description": "Updated description"}
        response = await async_client.patch(f"/api/v1/checklist/{item['taskId']}", json=update_data, headers=auth_headers_admin)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["taskId"] == item["taskId"]  # Should not change
    
    @pytest.mark.asyncio
    async def test_update_checklist_item_unauthorized(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_checklist_data):
        """Test updating checklist item by non-admin user fails."""
        # Create a test checklist item
        item = await create_test_checklist_item(clean_database, sample_checklist_data)
        
        update_data = {"description": "Updated description"}
        response = await async_client.patch(f"/api/v1/checklist/{item['taskId']}", json=update_data, headers=auth_headers_user)
        
        assert response.status_code == 403

class TestChecklistDeletion:
    """Test checklist item deletion functionality."""
    
    @pytest.mark.asyncio
    async def test_delete_checklist_item_success(self, async_client: AsyncClient, auth_headers_admin, clean_database, sample_checklist_data):
        """Test successful checklist item deletion by admin."""
        # Create a test checklist item
        item = await create_test_checklist_item(clean_database, sample_checklist_data)
        
        response = await async_client.delete(f"/api/v1/checklist/{item['taskId']}", headers=auth_headers_admin)
        
        assert response.status_code == 204
        
        # Verify item is deleted
        get_response = await async_client.get(f"/api/v1/checklist/{item['taskId']}", headers=auth_headers_admin)
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_checklist_item_unauthorized(self, async_client: AsyncClient, auth_headers_user, clean_database, sample_checklist_data):
        """Test checklist item deletion by non-admin user fails."""
        # Create a test checklist item
        item = await create_test_checklist_item(clean_database, sample_checklist_data)
        
        response = await async_client.delete(f"/api/v1/checklist/{item['taskId']}", headers=auth_headers_user)
        
        assert response.status_code == 403

class TestChecklistValidationLogic:
    """Test the specific checklist validation logic from project specifications."""
    
    @pytest.mark.asyncio
    async def test_cannot_complete_non_critical_if_critical_incomplete(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test that non-critical tasks cannot be completed if critical ones remain incomplete."""
        # Create critical (incomplete) and non-critical items
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": False}
        non_critical_item = {"taskId": "NORMAL-001", "description": "Normal task", "category": "backup", "isCritical": False, "completed": False}
        
        await create_test_checklist_item(clean_database, critical_item)
        non_critical = await create_test_checklist_item(clean_database, non_critical_item)
        
        # Try to complete non-critical task while critical task is incomplete
        completion_data = {"completed": True}
        response = await async_client.put(f"/api/v1/checklist/{non_critical['taskId']}", json=completion_data, headers=auth_headers_user)
        
        # This should fail according to project specifications
        assert response.status_code == 400
        assert "critical tasks must be completed first" in response.json()["detail"]["message"].lower()
    
    @pytest.mark.asyncio
    async def test_can_complete_non_critical_if_all_critical_complete(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test that non-critical tasks can be completed when all critical ones are complete."""
        # Create critical (completed) and non-critical items
        critical_item = {"taskId": "CRITICAL-001", "description": "Critical task", "category": "safety", "isCritical": True, "completed": True}
        non_critical_item = {"taskId": "NORMAL-001", "description": "Normal task", "category": "backup", "isCritical": False, "completed": False}
        
        await create_test_checklist_item(clean_database, critical_item)
        non_critical = await create_test_checklist_item(clean_database, non_critical_item)
        
        # Try to complete non-critical task when all critical tasks are complete
        completion_data = {"completed": True}
        response = await async_client.put(f"/api/v1/checklist/{non_critical['taskId']}", json=completion_data, headers=auth_headers_user)
        
        # This should succeed
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == True
    
    @pytest.mark.asyncio
    async def test_critical_tasks_can_always_be_completed(self, async_client: AsyncClient, auth_headers_user, clean_database):
        """Test that critical tasks can always be completed regardless of other task states."""
        # Create multiple critical items
        critical_item1 = {"taskId": "CRITICAL-001", "description": "Critical task 1", "category": "safety", "isCritical": True, "completed": False}
        critical_item2 = {"taskId": "CRITICAL-002", "description": "Critical task 2", "category": "security", "isCritical": True, "completed": False}
        
        critical1 = await create_test_checklist_item(clean_database, critical_item1)
        await create_test_checklist_item(clean_database, critical_item2)
        
        # Complete one critical task while another remains incomplete
        completion_data = {"completed": True}
        response = await async_client.put(f"/api/v1/checklist/{critical1['taskId']}", json=completion_data, headers=auth_headers_user)
        
        # This should succeed
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == True