# Testing Configuration for Smart Lab Power Shutdown Assistant Backend

import os
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient

# Add the project root to Python path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from config.settings import settings
from config.database import db

# Test Database Configuration
TEST_MONGODB_URL = "mongodb://localhost:27017"
TEST_DATABASE_NAME = "smart_lab_shutdown_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_db():
    """Setup test database connection."""
    # Override database settings for testing
    original_url = settings.MONGODB_URL
    original_db_name = settings.MONGODB_DATABASE_NAME
    
    settings.MONGODB_URL = TEST_MONGODB_URL
    settings.MONGODB_DATABASE_NAME = TEST_DATABASE_NAME
    
    # Connect to test database
    client = AsyncIOMotorClient(TEST_MONGODB_URL)
    test_database = client[TEST_DATABASE_NAME]
    
    # Store original database instance
    original_database = db.database
    db.database = test_database
    
    yield test_database
    
    # Cleanup: Drop test database
    await client.drop_database(TEST_DATABASE_NAME)
    client.close()
    
    # Restore original settings
    settings.MONGODB_URL = original_url
    settings.MONGODB_DATABASE_NAME = original_db_name
    db.database = original_database

@pytest_asyncio.fixture
async def async_client(test_db):
    """Create async client for testing FastAPI endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def client():
    """Create sync client for testing FastAPI endpoints."""
    return TestClient(app)

@pytest_asyncio.fixture
async def clean_database(test_db):
    """Clean database before each test."""
    # Clear all collections
    collections = await test_db.list_collection_names()
    for collection_name in collections:
        await test_db[collection_name].delete_many({})
    yield test_db

# Test Data Fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "engineer"
    }

@pytest.fixture
def sample_admin_data():
    """Sample admin user data for testing."""
    return {
        "username": "testadmin",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Test Admin",
        "role": "admin"
    }

@pytest.fixture
def sample_device_data():
    """Sample device data for testing."""
    return {
        "deviceId": "TEST-001",
        "name": "Test Server",
        "type": "server",
        "location": "Test Rack",
        "status": "on",
        "assignedUsers": [],
        "specifications": {
            "cpu": "Test CPU",
            "ram": "16GB",
            "storage": "500GB SSD"
        }
    }

@pytest.fixture
def sample_checklist_data():
    """Sample checklist item data for testing."""
    return {
        "taskId": "TEST-TASK-001",
        "description": "Test critical task",
        "category": "safety",
        "isCritical": True,
        "completed": False,
        "instructions": "Test instructions",
        "estimatedDuration": 10
    }

# Authentication Helpers
@pytest_asyncio.fixture
async def auth_headers_user(async_client, sample_user_data, clean_database):
    """Get authentication headers for regular user."""
    # Register user
    response = await async_client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"]
    }
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def auth_headers_admin(async_client, sample_admin_data, clean_database):
    """Get authentication headers for admin user."""
    # Register admin
    response = await async_client.post("/api/v1/auth/register", json=sample_admin_data)
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "username": sample_admin_data["username"],
        "password": sample_admin_data["password"]
    }
    response = await async_client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Database Helper Functions
async def create_test_user(database, user_data):
    """Helper to create a test user in database."""
    from src.models.user import UserInDB
    from passlib.context import CryptContext
    from datetime import datetime
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user_in_db = {
        **user_data,
        "hashed_password": pwd_context.hash(user_data["password"]),
        "is_active": True,
        "assignedDevices": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    del user_in_db["password"]
    
    result = await database.users.insert_one(user_in_db)
    user_in_db["_id"] = result.inserted_id
    return user_in_db

async def create_test_device(database, device_data):
    """Helper to create a test device in database."""
    from datetime import datetime
    
    device_in_db = {
        **device_data,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await database.devices.insert_one(device_in_db)
    device_in_db["_id"] = result.inserted_id
    return device_in_db

async def create_test_checklist_item(database, checklist_data):
    """Helper to create a test checklist item in database."""
    from datetime import datetime
    
    checklist_in_db = {
        **checklist_data,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await database.checklist.insert_one(checklist_in_db)
    checklist_in_db["_id"] = result.inserted_id
    return checklist_in_db

# Test Utilities
def assert_user_response(response_data, expected_user_data):
    """Assert user response matches expected data."""
    assert response_data["username"] == expected_user_data["username"]
    assert response_data["email"] == expected_user_data["email"]
    assert response_data["full_name"] == expected_user_data["full_name"]
    assert response_data["role"] == expected_user_data["role"]
    assert "hashed_password" not in response_data  # Password should not be exposed

def assert_device_response(response_data, expected_device_data):
    """Assert device response matches expected data."""
    assert response_data["deviceId"] == expected_device_data["deviceId"]
    assert response_data["name"] == expected_device_data["name"]
    assert response_data["type"] == expected_device_data["type"]
    assert response_data["location"] == expected_device_data["location"]
    assert response_data["status"] == expected_device_data["status"]

def assert_checklist_response(response_data, expected_checklist_data):
    """Assert checklist response matches expected data."""
    assert response_data["taskId"] == expected_checklist_data["taskId"]
    assert response_data["description"] == expected_checklist_data["description"]
    assert response_data["category"] == expected_checklist_data["category"]
    assert response_data["isCritical"] == expected_checklist_data["isCritical"]