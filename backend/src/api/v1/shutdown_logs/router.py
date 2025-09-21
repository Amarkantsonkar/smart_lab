from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from config.database import get_database
from src.models.shutdown import ShutdownCreate, ShutdownResponse
from src.auth import get_current_user, require_role

router = APIRouter(prefix="", tags=["shutdown-logs"])

@router.post("/", response_model=ShutdownResponse, status_code=status.HTTP_201_CREATED)
async def create_shutdown_log(log: ShutdownCreate, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Create log document
    log_dict = log.dict()
    
    # Insert log into database
    result = await db.get_collection("shutdownLogs").insert_one(log_dict)
    created_log = await db.get_collection("shutdownLogs").find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string for JSON serialization
    created_log["id"] = str(created_log.pop("_id"))
    created_log["timestamp"] = created_log["timestamp"].isoformat()
    
    return created_log

@router.get("/", response_model=List[ShutdownResponse])
async def read_shutdown_logs(
    skip: int = 0, 
    limit: int = 100, 
    device: Optional[str] = None,
    user: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db = Depends(get_database), 
    current_user: dict = Depends(get_current_user)
):
    # Build query filter
    query_filter = {}
    
    if device:
        query_filter["device"] = device
    if user:
        query_filter["user"] = user
    
    # Handle date filtering
    if start_date or end_date:
        timestamp_filter = {}
        if start_date:
            timestamp_filter["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            timestamp_filter["$lte"] = datetime.fromisoformat(end_date)
        if timestamp_filter:
            query_filter["timestamp"] = timestamp_filter
    
    logs_cursor = db.get_collection("shutdownLogs").find(query_filter).skip(skip).limit(limit)
    logs = []
    async for log in logs_cursor:
        log["id"] = str(log.pop("_id"))
        log["timestamp"] = log["timestamp"].isoformat()
        logs.append(log)
    
    return logs

@router.get("/{log_id}", response_model=ShutdownResponse)
async def read_shutdown_log(log_id: str, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    log = await db.get_collection("shutdownLogs").find_one({"logId": log_id})
    if not log:
        raise HTTPException(status_code=404, detail="Shutdown log not found")
    
    log["id"] = str(log.pop("_id"))
    log["timestamp"] = log["timestamp"].isoformat()
    
    return log