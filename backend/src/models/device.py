from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DeviceBase(BaseModel):
    deviceId: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Device name")
    status: str = Field(default="on", description="Device power status: on, off, maintenance")

class DeviceCreate(DeviceBase):
    location: Optional[str] = Field(None, description="Physical location of the device")

class DeviceUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Updated device power status")
    location: Optional[str] = Field(None, description="Updated physical location")

class DeviceInDB(DeviceBase):
    id: str = Field(..., alias="_id", description="Device ID")
    location: Optional[str] = Field(None, description="Physical location of the device")
    lastShutdown: Optional[datetime] = Field(None, description="Timestamp of last shutdown")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Device creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DeviceResponse(DeviceBase):
    id: str = Field(..., alias="_id", description="Device ID")
    location: Optional[str] = Field(None, description="Physical location of the device")
    assignedUsers: Optional[list] = Field(default_factory=list, description="List of users assigned to this device")
    lastShutdown: Optional[datetime] = Field(None, description="Timestamp of last shutdown")
    lastStartup: Optional[datetime] = Field(None, description="Timestamp of last startup")
    createdAt: datetime = Field(..., description="Device creation timestamp")
    updatedAt: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }