#!/usr/bin/env python3
"""
MongoDB setup script for Smart Lab Power Shutdown Assistant
This script creates the necessary collections and indexes for the application.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

async def create_collections_and_indexes():
    """Create collections and indexes for the Smart Lab Power Shutdown Assistant"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE_NAME]
    
    print(f"Setting up MongoDB database: {settings.MONGODB_DATABASE_NAME}")
    print(f"MongoDB URL: {settings.MONGODB_URL}")
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # Users Collection
        print("\n📁 Setting up Users collection...")
        users_collection = db.users
        users_indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("username", ASCENDING)], unique=True),
            IndexModel([("role", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("is_active", ASCENDING)])
        ]
        await users_collection.create_indexes(users_indexes)
        print("✅ Users collection indexes created")
        
        # Devices Collection
        print("\n📁 Setting up Devices collection...")
        devices_collection = db.devices
        devices_indexes = [
            IndexModel([("deviceId", ASCENDING)], unique=True),
            IndexModel([("name", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("location", ASCENDING)]),
            IndexModel([("assignedUsers", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("lastShutdown", DESCENDING)])
        ]
        await devices_collection.create_indexes(devices_indexes)
        print("✅ Devices collection indexes created")
        
        # Checklist Collection
        print("\n📁 Setting up Checklist collection...")
        checklist_collection = db.checklist
        checklist_indexes = [
            IndexModel([("taskId", ASCENDING)], unique=True),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("isCritical", ASCENDING)]),
            IndexModel([("completed", ASCENDING)]),
            IndexModel([("completedBy", ASCENDING)]),
            IndexModel([("completedAt", DESCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            # Compound index for filtering
            IndexModel([("category", ASCENDING), ("isCritical", ASCENDING)]),
            IndexModel([("completed", ASCENDING), ("isCritical", ASCENDING)])
        ]
        await checklist_collection.create_indexes(checklist_indexes)
        print("✅ Checklist collection indexes created")
        
        # Shutdown Logs Collection
        print("\n📁 Setting up Shutdown Logs collection...")
        shutdown_logs_collection = db.shutdown_logs
        shutdown_logs_indexes = [
            IndexModel([("deviceId", ASCENDING)]),
            IndexModel([("userId", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("duration", ASCENDING)]),
            # Compound indexes for common queries
            IndexModel([("deviceId", ASCENDING), ("timestamp", DESCENDING)]),
            IndexModel([("userId", ASCENDING), ("timestamp", DESCENDING)]),
            IndexModel([("status", ASCENDING), ("timestamp", DESCENDING)]),
            IndexModel([("timestamp", DESCENDING), ("status", ASCENDING)])
        ]
        await shutdown_logs_collection.create_indexes(shutdown_logs_indexes)
        print("✅ Shutdown Logs collection indexes created")
        
        # Create initial data if collections are empty
        print("\n📊 Setting up initial data...")
        
        # Check if admin user exists
        admin_user = await users_collection.find_one({"role": "admin"})
        if not admin_user:
            await create_initial_admin(users_collection)
        
        # Check if sample devices exist
        device_count = await devices_collection.count_documents({})
        if device_count == 0:
            await create_sample_devices(devices_collection)
        
        # Check if checklist items exist
        checklist_count = await checklist_collection.count_documents({})
        if checklist_count == 0:
            await create_sample_checklist(checklist_collection)
        
        print("\n✅ MongoDB setup completed successfully!")
        
        # Print database statistics
        print("\n📊 Database Statistics:")
        collections = await db.list_collection_names()
        for collection_name in collections:
            count = await db[collection_name].count_documents({})
            print(f"  - {collection_name}: {count} documents")
            
    except Exception as e:
        print(f"❌ Error setting up MongoDB: {e}")
        raise
    finally:
        client.close()

async def create_initial_admin(users_collection):
    """Create initial admin user"""
    from passlib.context import CryptContext
    from datetime import datetime
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    admin_user = {
        "username": "admin",
        "email": "admin@smartlab.com",
        "hashed_password": pwd_context.hash("admin123"),  # Change in production!
        "full_name": "System Administrator",
        "role": "admin",
        "is_active": True,
        "assignedDevices": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await users_collection.insert_one(admin_user)
    print("👤 Created initial admin user (username: admin, password: admin123)")

async def create_sample_devices(devices_collection):
    """Create sample devices"""
    from datetime import datetime
    
    sample_devices = [
        {
            "deviceId": "SRV-001",
            "name": "Main Database Server",
            "type": "server",
            "location": "Rack A1",
            "status": "on",
            "assignedUsers": [],
            "specifications": {
                "cpu": "Intel Xeon E5-2690",
                "ram": "64GB",
                "storage": "2TB SSD"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "deviceId": "SRV-002", 
            "name": "Web Application Server",
            "type": "server",
            "location": "Rack A2",
            "status": "on",
            "assignedUsers": [],
            "specifications": {
                "cpu": "Intel Xeon E5-2680",
                "ram": "32GB", 
                "storage": "1TB SSD"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "deviceId": "NET-001",
            "name": "Core Network Switch",
            "type": "network",
            "location": "Network Closet",
            "status": "on",
            "assignedUsers": [],
            "specifications": {
                "ports": "48-port Gigabit",
                "type": "Managed Switch"
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await devices_collection.insert_many(sample_devices)
    print(f"🖥️  Created {len(sample_devices)} sample devices")

async def create_sample_checklist(checklist_collection):
    """Create sample checklist items"""
    from datetime import datetime
    
    sample_checklist = [
        {
            "taskId": "SAFETY-001",
            "description": "Verify all personnel have exited the lab area",
            "category": "safety",
            "isCritical": True,
            "completed": False,
            "instructions": "Check all rooms and ensure no personnel remain in the lab",
            "estimatedDuration": 5,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "taskId": "SAFETY-002",
            "description": "Secure all hazardous materials",
            "category": "safety",
            "isCritical": True,
            "completed": False,
            "instructions": "Ensure all chemical and biological materials are properly stored",
            "estimatedDuration": 10,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "taskId": "BACKUP-001",
            "description": "Complete database backup",
            "category": "backup",
            "isCritical": True,
            "completed": False,
            "instructions": "Run full database backup and verify integrity",
            "estimatedDuration": 30,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "taskId": "SECURITY-001",
            "description": "Lock all access points",
            "category": "security",
            "isCritical": True,
            "completed": False,
            "instructions": "Ensure all doors and windows are secured",
            "estimatedDuration": 5,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "taskId": "NETWORK-001",
            "description": "Verify network connectivity",
            "category": "network",
            "isCritical": False,
            "completed": False,
            "instructions": "Test network connections and document any issues",
            "estimatedDuration": 15,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    await checklist_collection.insert_many(sample_checklist)
    print(f"📋 Created {len(sample_checklist)} sample checklist items")

def print_atlas_setup_instructions():
    """Print instructions for MongoDB Atlas setup"""
    print("\n" + "="*60)
    print("🌐 MONGODB ATLAS SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. Create MongoDB Atlas Account:")
    print("   - Go to https://www.mongodb.com/cloud/atlas")
    print("   - Sign up for a free account")
    
    print("\n2. Create a New Cluster:")
    print("   - Click 'Build a Database'")
    print("   - Choose 'FREE' tier (M0 Sandbox)")
    print("   - Select your preferred cloud provider and region")
    print("   - Name your cluster (e.g., 'smart-lab-cluster')")
    
    print("\n3. Configure Database Access:")
    print("   - Go to 'Database Access' in the left sidebar")
    print("   - Click 'Add New Database User'")
    print("   - Choose 'Password' authentication")
    print("   - Create username and password")
    print("   - Grant 'Atlas Admin' privileges")
    
    print("\n4. Configure Network Access:")
    print("   - Go to 'Network Access' in the left sidebar")
    print("   - Click 'Add IP Address'")
    print("   - For development: Add '0.0.0.0/0' (Allow access from anywhere)")
    print("   - For production: Add your specific IP addresses")
    
    print("\n5. Get Connection String:")
    print("   - Go to 'Databases' and click 'Connect'")
    print("   - Choose 'Connect your application'")
    print("   - Select 'Python' and version '3.6 or later'")
    print("   - Copy the connection string")
    
    print("\n6. Update Environment Variables:")
    print("   Replace in backend/.env:")
    print("   MONGODB_URL=mongodb+srv://<username>:<password>@<cluster-url>/<database>")
    print("   MONGODB_DATABASE_NAME=smart_lab_shutdown")
    
    print("\n7. Install Required Dependencies:")
    print("   pip install motor pymongo[srv] dnspython")
    
    print("\n8. Run This Setup Script:")
    print("   python scripts/setup_mongodb.py")
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🚀 Smart Lab Power Shutdown Assistant - MongoDB Setup")
    print("="*55)
    
    if "mongodb+srv://" in settings.MONGODB_URL or "atlas" in settings.MONGODB_URL.lower():
        print("🌐 Detected MongoDB Atlas configuration")
    elif "localhost" in settings.MONGODB_URL:
        print("🏠 Detected local MongoDB configuration")
    else:
        print("📋 MongoDB configuration detected")
    
    try:
        asyncio.run(create_collections_and_indexes())
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\n📚 If you haven't set up MongoDB Atlas yet:")
        print_atlas_setup_instructions()
        sys.exit(1)