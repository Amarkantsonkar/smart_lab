#!/usr/bin/env python3
"""
Database migration script for Smart Lab Power Shutdown Assistant
This script handles database schema updates and data migrations.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

class DatabaseMigrator:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.MONGODB_DATABASE_NAME]
        
        # Test connection
        await self.client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")
    
    async def run_migrations(self):
        """Run all pending migrations"""
        print("🔄 Running database migrations...")
        
        # Create migrations tracking collection if it doesn't exist
        migrations_collection = self.db.migrations
        
        # List of all migrations in order
        migrations = [
            "001_initial_schema",
            "002_add_user_preferences", 
            "003_add_device_metadata",
            "004_add_checklist_dependencies",
            "005_add_audit_logs"
        ]
        
        for migration_name in migrations:
            # Check if migration already applied
            existing = await migrations_collection.find_one({"name": migration_name})
            if existing:
                print(f"⏭️  Skipping {migration_name} (already applied)")
                continue
                
            print(f"🔧 Applying migration: {migration_name}")
            migration_method = getattr(self, f"migration_{migration_name}", None)
            
            if migration_method:
                try:
                    await migration_method()
                    
                    # Record successful migration
                    await migrations_collection.insert_one({
                        "name": migration_name,
                        "applied_at": datetime.utcnow(),
                        "status": "success"
                    })
                    print(f"✅ Applied {migration_name}")
                    
                except Exception as e:
                    print(f"❌ Failed to apply {migration_name}: {e}")
                    # Record failed migration
                    await migrations_collection.insert_one({
                        "name": migration_name,
                        "applied_at": datetime.utcnow(),
                        "status": "failed",
                        "error": str(e)
                    })
                    raise
            else:
                print(f"⚠️  Migration method not found for {migration_name}")
        
        print("✅ All migrations completed successfully")
    
    async def migration_001_initial_schema(self):
        """Initial schema setup - already handled by setup_mongodb.py"""
        pass
    
    async def migration_002_add_user_preferences(self):
        """Add user preferences field to users collection"""
        users_collection = self.db.users
        
        # Add preferences field to all users who don't have it
        await users_collection.update_many(
            {"preferences": {"$exists": False}},
            {"$set": {
                "preferences": {
                    "theme": "light",
                    "notifications": {
                        "email": True,
                        "browser": True,
                        "shutdown_alerts": True
                    },
                    "dashboard": {
                        "auto_refresh": True,
                        "refresh_interval": 30
                    }
                },
                "updated_at": datetime.utcnow()
            }}
        )
    
    async def migration_003_add_device_metadata(self):
        """Add metadata fields to devices collection"""
        devices_collection = self.db.devices
        
        # Add metadata fields to all devices
        await devices_collection.update_many(
            {"metadata": {"$exists": False}},
            {"$set": {
                "metadata": {
                    "manufacturer": "",
                    "model": "",
                    "serial_number": "",
                    "purchase_date": None,
                    "warranty_expires": None,
                    "maintenance_schedule": "monthly"
                },
                "power_consumption": {
                    "watts": 0,
                    "estimated_monthly_cost": 0
                },
                "updated_at": datetime.utcnow()
            }}
        )
    
    async def migration_004_add_checklist_dependencies(self):
        """Add dependency tracking to checklist items"""
        checklist_collection = self.db.checklist
        
        # Add dependencies field to all checklist items
        await checklist_collection.update_many(
            {"dependencies": {"$exists": False}},
            {"$set": {
                "dependencies": [],  # Array of taskIds that must be completed first
                "priority": 1,       # 1=low, 2=medium, 3=high, 4=critical
                "updated_at": datetime.utcnow()
            }}
        )
    
    async def migration_005_add_audit_logs(self):
        """Create audit logs collection for tracking all system changes"""
        audit_logs_collection = self.db.audit_logs
        
        # Create index for audit logs
        from pymongo import IndexModel, ASCENDING, DESCENDING
        
        audit_indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("action", ASCENDING)]),
            IndexModel([("resource_type", ASCENDING)]),
            IndexModel([("resource_id", ASCENDING)]),
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("timestamp", DESCENDING), ("user_id", ASCENDING)])
        ]
        
        await audit_logs_collection.create_indexes(audit_indexes)
        
        # Insert initial audit log entry
        await audit_logs_collection.insert_one({
            "user_id": "system",
            "action": "migration_completed",
            "resource_type": "database",
            "resource_id": "audit_logs_setup",
            "timestamp": datetime.utcnow(),
            "details": {
                "migration": "005_add_audit_logs",
                "description": "Audit logs collection created and indexed"
            }
        })

async def main():
    """Main migration runner"""
    print("🚀 Smart Lab Power Shutdown Assistant - Database Migration")
    print("="*60)
    
    migrator = DatabaseMigrator()
    
    try:
        await migrator.connect()
        await migrator.run_migrations()
        
        print("\n📊 Migration Summary:")
        migrations_collection = migrator.db.migrations
        
        # Count successful migrations
        success_count = await migrations_collection.count_documents({"status": "success"})
        failed_count = await migrations_collection.count_documents({"status": "failed"})
        
        print(f"  ✅ Successful migrations: {success_count}")
        print(f"  ❌ Failed migrations: {failed_count}")
        
        if failed_count > 0:
            print("\n⚠️  Some migrations failed. Check the migrations collection for details.")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        await migrator.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Migration interrupted by user")
        sys.exit(1)