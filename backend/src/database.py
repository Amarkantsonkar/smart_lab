from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
from typing import AsyncGenerator
import os

from config.settings import settings

class Database:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db = None
    
    async def connect_to_database(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
    
    async def close_database_connection(self):
        if self.client:
            self.client.close()
    
    def get_collection(self, collection_name: str):
        return self.db[collection_name]

# Create database instance
db = Database()

# Dependency to get database client
async def get_database() -> AsyncGenerator[AsyncIOMotorClient, None]:
    await db.connect_to_database()
    try:
        yield db
    finally:
        await db.close_database_connection()