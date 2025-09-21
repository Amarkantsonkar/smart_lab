from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict
from datetime import timedelta

from config.settings import settings
from src.models.user import UserCreate, UserResponse, UserProfileUpdate
from src.auth import oauth2_scheme, get_current_user, require_role
from config.database import get_database
from src.api.v1.auth.schemas import Token
from src.auth.jwt import create_access_token
from passlib.context import CryptContext

router = APIRouter(prefix="", tags=["authentication"])

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return crypt_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return crypt_context.hash(password)

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db = Depends(get_database)):
    # Check if user already exists
    existing_user = await db.get_collection("users").find_one({"name": user.name})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create user document
    from datetime import datetime
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["createdAt"] = datetime.utcnow()
    user_dict["updatedAt"] = datetime.utcnow()
    
    # Insert user into database
    result = await db.get_collection("users").insert_one(user_dict)
    created_user = await db.get_collection("users").find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string for JSON serialization
    created_user["id"] = str(created_user.pop("_id"))
    created_user["createdAt"] = created_user["createdAt"].isoformat()
    created_user["updatedAt"] = created_user["updatedAt"].isoformat()
    
    return created_user

@router.post("/login", response_model=Token)
async def login(username: str = Body(...), password: str = Body(...), db = Depends(get_database)):
    # Find user by username
    user = await db.get_collection("users").find_one({"name": username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["name"], "role": user["role"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Dict = Depends(get_current_user), db = Depends(get_database)):
    # Get user from database
    user = await db.get_collection("users").find_one({"name": current_user["sub"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare response
    user_response = {
        "id": str(user["_id"]),
        "name": user["name"],
        "role": user["role"],
        "assignedDevices": user.get("assignedDevices", []),
        "createdAt": user["createdAt"].isoformat(),
        "updatedAt": user["updatedAt"].isoformat()
    }
    
    return user_response

@router.put("/profile", response_model=UserResponse)
async def update_profile(profile_update: UserProfileUpdate, current_user: Dict = Depends(get_current_user), db = Depends(get_database)):
    """Update current user's profile"""
    from datetime import datetime
    
    # Get current user from database
    user = await db.get_collection("users").find_one({"name": current_user["sub"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare update data
    update_data = {}
    
    if profile_update.name is not None:
        # Check if new username is already taken by another user
        existing_user = await db.get_collection("users").find_one({
            "name": profile_update.name,
            "_id": {"$ne": user["_id"]}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_data["name"] = profile_update.name
    
    if profile_update.password is not None:
        # Hash the new password
        update_data["password"] = get_password_hash(profile_update.password)
    
    if update_data:
        update_data["updatedAt"] = datetime.utcnow()
        
        # Update user in database
        await db.get_collection("users").update_one(
            {"name": current_user["sub"]}, 
            {"$set": update_data}
        )
    
    # Get updated user
    updated_user = await db.get_collection("users").find_one({"name": profile_update.name or current_user["sub"]})
    
    # Prepare response
    user_response = {
        "id": str(updated_user["_id"]),
        "name": updated_user["name"],
        "role": updated_user["role"],
        "assignedDevices": updated_user.get("assignedDevices", []),
        "createdAt": updated_user["createdAt"].isoformat(),
        "updatedAt": updated_user["updatedAt"].isoformat()
    }
    
    return user_response