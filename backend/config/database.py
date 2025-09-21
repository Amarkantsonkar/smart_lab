from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, HTTPException, status
from typing import AsyncGenerator
import os

from config.settings import settings

class Database:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
    
    async def connect_to_database(self):
        try:
            # Skip database connection if using placeholder URL
            if "username:password" in settings.MONGODB_URL:
                print("⚠️  Skipping MongoDB connection - placeholder URL detected")
                print("📝 Please configure your MongoDB Atlas connection string in .env file")
                return
                
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DATABASE_NAME]
            # Test the connection
            await self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
        except Exception as e:
            print(f"⚠️  Failed to connect to MongoDB: {e}")
            print("📝 Please check your MongoDB configuration")
            print("📝 Make sure MongoDB is running on localhost:27017")
            # Don't raise exception to allow server to start
            # raise HTTPException(
            #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #     detail="Database connection failed"
            # )
    
    async def close_database_connection(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")
    
    def get_collection(self, collection_name: str):
        return self.db[collection_name]

# Create database instance
db = Database()

# Dependency to get database client
async def get_database() -> AsyncGenerator[Database, None]:
    # Ensure database is connected
    if not db.client:
        await db.connect_to_database()
    yield db