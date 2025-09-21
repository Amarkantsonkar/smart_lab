from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ShutdownBase(BaseModel):
    device: str = Field(..., description="Device ID being shut down")
    user: str = Field(..., description="User ID initiating the shutdown")
    userName: str = Field(..., description="Username initiating the shutdown")
    status: str = Field(..., description="Shutdown status: success or failed")

class ShutdownCreate(ShutdownBase):
    reason: Optional[str] = Field(None, description="Reason for failure if shutdown failed")
    duration: int = Field(default=0, description="Duration of shutdown process in seconds")

class ShutdownInDB(ShutdownBase):
    id: str = Field(..., alias="_id", description="Shutdown log ID")
    logId: str = Field(..., description="Unique log identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of shutdown attempt")
    duration: int = Field(default=0, description="Duration of shutdown process in seconds")
    reason: Optional[str] = Field(None, description="Reason for failure if shutdown failed")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ShutdownResponse(ShutdownBase):
    id: str = Field(..., alias="_id", description="Shutdown log ID")
    logId: str = Field(..., description="Unique log identifier")
    timestamp: datetime = Field(..., description="Timestamp of shutdown attempt")
    duration: int = Field(..., description="Duration of shutdown process in seconds")
    reason: Optional[str] = Field(None, description="Reason for failure if shutdown failed")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }