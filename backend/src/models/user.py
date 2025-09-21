from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., description="User's unique username")
    role: str = Field(..., description="User role: Engineer or Admin")

class UserCreate(UserBase):
    password: str = Field(..., description="User password")
    assignedDevices: List[str] = Field(default=[], description="List of device IDs assigned to the user")

class UserUpdate(BaseModel):
    assignedDevices: Optional[List[str]] = Field(None, description="Updated list of assigned devices")
    role: Optional[str] = Field(None, description="Updated user role")

class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Updated username")
    password: Optional[str] = Field(None, description="Updated password")

class UserInDB(UserBase):
    id: str = Field(..., alias="_id", description="User ID")
    assignedDevices: List[str] = Field(default=[], description="List of device IDs assigned to the user")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="User creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserResponse(UserBase):
    id: str = Field(..., alias="_id", description="User ID")
    assignedDevices: List[str] = Field(default=[], description="List of device IDs assigned to the user")
    createdAt: datetime = Field(..., description="User creation timestamp")
    updatedAt: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }