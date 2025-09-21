#!/usr/bin/env python3
"""
Demo User Creation Script
Creates admin and engineer accounts for testing the Smart Lab Power Shutdown Assistant
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.password_utils import hash_password

# Demo users data
DEMO_USERS = {
    "admin": {
        "username": "admin",
        "email": "admin@smartlab.com",
        "password": "admin123",
        "role": "admin"
    },
    "engineer": {
        "username": "engineer",
        "email": "engineer@smartlab.com", 
        "password": "engineer123",
        "role": "engineer"
    }
}

# In-memory user store (since we don't have DB connection yet)
users_store = {}

async def create_demo_users():
    """Create demo users in memory store"""
    print("🔧 Creating demo user accounts...")
    print("=" * 50)
    
    for user_type, user_data in DEMO_USERS.items():
        # Hash the password
        hashed_password = hash_password(user_data["password"])
        
        # Create user record
        user_record = {
            "id": f"demo_{user_type}",
            "username": user_data["username"],
            "email": user_data["email"],
            "password_hash": hashed_password,
            "role": user_data["role"],
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Store in memory
        users_store[user_data["username"]] = user_record
        
        print(f"✅ Created {user_type.upper()} account:")
        print(f"   Username: {user_data['username']}")
        print(f"   Password: {user_data['password']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Role: {user_data['role']}")
        print()
    
    print("🎉 Demo accounts created successfully!")
    print("=" * 50)
    print("\n📝 CREDENTIALS FOR TESTING:")
    print("=" * 30)
    print("👑 ADMIN ACCOUNT:")
    print(f"   Username: {DEMO_USERS['admin']['username']}")
    print(f"   Password: {DEMO_USERS['admin']['password']}")
    print()
    print("🔧 ENGINEER ACCOUNT:")
    print(f"   Username: {DEMO_USERS['engineer']['username']}")
    print(f"   Password: {DEMO_USERS['engineer']['password']}")
    print()
    print("🌐 Login at: http://localhost:5173")
    print("🔗 API docs: http://localhost:8000/docs")
    
    return users_store

if __name__ == "__main__":
    # Run the demo user creation
    users = asyncio.run(create_demo_users())
    
    # Save to a simple file for the backend to load
    import json
    demo_users_file = os.path.join(os.path.dirname(__file__), "demo_users.json")
    
    # Convert datetime objects to strings for JSON serialization
    serializable_users = {}
    for username, user_data in users.items():
        serializable_users[username] = {
            **user_data,
            "created_at": user_data["created_at"].isoformat()
        }
    
    with open(demo_users_file, "w") as f:
        json.dump(serializable_users, f, indent=2)
    
    print(f"\n💾 Demo users saved to: {demo_users_file}")
    print("\n🚀 You can now login with the credentials above!")