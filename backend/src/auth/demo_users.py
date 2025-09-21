# Demo users for testing without database connection
from datetime import datetime
from passlib.context import CryptContext

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

# Pre-hashed passwords for demo users
DEMO_USERS = {
    "admin": {
        "id": "demo_admin",
        "username": "admin", 
        "email": "admin@smartlab.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj1o3P.RNOyq",  # admin123
        "role": "admin",
        "created_at": datetime.utcnow(),
        "is_active": True
    },
    "engineer": {
        "id": "demo_engineer",
        "username": "engineer",
        "email": "engineer@smartlab.com", 
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj1o3P.RNOyq",  # engineer123
        "role": "engineer",
        "created_at": datetime.utcnow(),
        "is_active": True
    }
}

def get_demo_user(username: str):
    """Get demo user by username"""
    return DEMO_USERS.get(username)

def verify_demo_user(username: str, password: str):
    """Verify demo user credentials"""
    user = get_demo_user(username)
    if not user:
        return None
    
    if verify_password(password, user["password_hash"]):
        return user
    return None