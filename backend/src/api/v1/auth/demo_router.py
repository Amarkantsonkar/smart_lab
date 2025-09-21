from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict
from datetime import timedelta

from config.settings import settings
from src.auth.demo_users import verify_demo_user, get_demo_user
from src.auth.jwt import create_access_token

router = APIRouter(tags=["authentication"])

@router.post("/login")
async def login_demo(form_data: OAuth2PasswordRequestForm = None, username: str = None, password: str = None):
    """Demo login endpoint that works without database"""
    
    # Handle both form data and JSON body
    if form_data:
        username = form_data.username
        password = form_data.password
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    # Verify demo user
    user = verify_demo_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@router.get("/me")
async def get_current_user_demo():
    """Get current user info (demo version)"""
    # For demo purposes, return admin user
    user = get_demo_user("admin")
    return {
        "id": user["id"],
        "username": user["username"], 
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"].isoformat()
    }

@router.get("/demo-users")
async def get_demo_users():
    """Get available demo users for testing"""
    return {
        "demo_users": [
            {
                "username": "admin",
                "password": "admin123", 
                "role": "admin",
                "description": "Administrator account with full access"
            },
            {
                "username": "engineer",
                "password": "engineer123",
                "role": "engineer", 
                "description": "Engineer account with limited access"
            }
        ],
        "note": "These are demo credentials for testing without database connection"
    }