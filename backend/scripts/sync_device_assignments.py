#!/usr/bin/env python3
"""
Data Migration Script: Sync Device Assignments

This script fixes the data consistency issue where device assignments
are stored in users.assignedDevices but not reflected in devices.assignedUsers.

It syncs the assignments bi-directionally to ensure both collections
have consistent data.
"""

import asyncio
import sys
import os

# Add the backend root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

async def sync_device_assignments():
    """Sync device assignments between users and devices collections"""
    
    print("🔄 Starting device assignment synchronization...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
        # First, clear all assignedUsers from devices (we'll rebuild them)
        print("🧹 Clearing existing assignedUsers from devices...")
        await db.get_collection("devices").update_many(
            {},
            {"$set": {"assignedUsers": []}}
        )
        
        # Get all users with assigned devices
        print("👥 Processing user assignments...")
        users_processed = 0
        devices_updated = 0
        
        async for user in db.get_collection("users").find({"assignedDevices": {"$exists": True, "$ne": []}}):
            user_name = user["name"]
            assigned_devices = user.get("assignedDevices", [])
            
            if assigned_devices:
                print(f"  📋 User '{user_name}' has {len(assigned_devices)} devices: {assigned_devices}")
                
                # Update each assigned device to include this user
                for device_id in assigned_devices:
                    result = await db.get_collection("devices").update_one(
                        {"deviceId": device_id},
                        {"$addToSet": {"assignedUsers": user_name}}
                    )
                    if result.modified_count > 0:
                        devices_updated += 1
                        print(f"    ✅ Added '{user_name}' to device '{device_id}'")
                    else:
                        print(f"    ⚠️  Device '{device_id}' not found or already updated")
                
                users_processed += 1
        
        # Verify the sync by checking devices
        print("\n📊 Verification - Devices with assignments:")
        async for device in db.get_collection("devices").find({"assignedUsers": {"$ne": []}}):
            print(f"  🖥️  Device '{device['deviceId']}' ({device['name']}) assigned to: {device.get('assignedUsers', [])}")
        
        print(f"\n✅ Synchronization complete!")
        print(f"   📈 Users processed: {users_processed}")
        print(f"   📈 Device assignments updated: {devices_updated}")
        
        # Show summary statistics
        total_users = await db.get_collection("users").count_documents({})
        total_devices = await db.get_collection("devices").count_documents({})
        devices_with_assignments = await db.get_collection("devices").count_documents({"assignedUsers": {"$ne": []}})
        
        print(f"\n📊 Database Summary:")
        print(f"   👥 Total users: {total_users}")
        print(f"   🖥️  Total devices: {total_devices}")
        print(f"   🔗 Devices with assignments: {devices_with_assignments}")
        
    except Exception as e:
        print(f"❌ Error during synchronization: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(sync_device_assignments())