from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChecklistBase(BaseModel):
    taskId: str = Field(..., description="Unique task identifier")
    description: str = Field(..., description="Task description")
    category: str = Field(..., description="Task category: safety, security, backup, network")
    isCritical: bool = Field(default=True, description="Whether the task is critical for shutdown")

class ChecklistCreate(ChecklistBase):
    pass
class ChecklistUpdate(BaseModel):
    completed: Optional[bool] = Field(None, description="Completion status of the task")
    completedBy: Optional[str] = Field(None, description="User who completed the task")
    completedAt: Optional[datetime] = Field(None, description="Timestamp when task was completed")

class ChecklistInDB(ChecklistBase):
    id: str = Field(..., alias="_id", description="Checklist item ID")
    completed: bool = Field(default=False, description="Completion status of the task")
    completedBy: Optional[str] = Field(None, description="User who completed the task")
    completedAt: Optional[datetime] = Field(None, description="Timestamp when task was completed")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="Task creation timestamp")
    updatedAt: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ChecklistResponse(ChecklistBase):
    id: str = Field(..., alias="_id", description="Checklist item ID")
    completed: bool = Field(..., description="Completion status of the task")
    completedBy: Optional[str] = Field(None, description="User who completed the task")
    completedAt: Optional[datetime] = Field(None, description="Timestamp when task was completed")
    createdAt: datetime = Field(..., description="Task creation timestamp")
    updatedAt: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }