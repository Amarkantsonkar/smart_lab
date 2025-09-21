from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from datetime import datetime, timedelta
import asyncio

from config.database import get_database
from src.models.shutdown import ShutdownCreate
from src.auth import get_current_user

router = APIRouter(prefix="", tags=["shutdown"])

@router.post("/validate-checklist")
async def validate_checklist(db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Get all critical checklist items
    critical_items_cursor = db.get_collection("checklist").find({"isCritical": True})
    critical_items = []
    async for item in critical_items_cursor:
        critical_items.append(item)
    
    # Check if any critical items are not completed
    incomplete_items = [item for item in critical_items if not item.get("completed", False)]
    
    if incomplete_items:
        return {
            "allCompleted": False,
            "totalCriticalItems": len(critical_items),
            "completedItems": len(critical_items) - len(incomplete_items),
            "incompleteItems": [
                {
                    "taskId": item["taskId"],
                    "description": item["description"]
                } for item in incomplete_items
            ]
        }
    
    return {
        "allCompleted": True,
        "totalCriticalItems": len(critical_items),
        "completedItems": len(critical_items),
        "incompleteItems": []
    }

@router.post("/initiate/{device_id}")
async def initiate_shutdown(device_id: str, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Verify the user has access to this device
    user_devices = await db.get_collection("users").find_one(
        {"name": current_user["sub"], "assignedDevices": {"$in": [device_id]}}
    )
    if not user_devices:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to shutdown this device"
        )
    
    # Validate checklist before shutdown
    validation_result = await validate_checklist(db, current_user)
    if not validation_result["allCompleted"]:
        # Create failed shutdown log
        shutdown_log = ShutdownCreate(
            device=device_id,
            user=current_user["sub"],
            userName=current_user["sub"],
            status="failed",
            reason="Critical checklist items not completed"
        ).dict()
        
        shutdown_log["logId"] = f"log-{datetime.utcnow().timestamp()}"
        shutdown_log["timestamp"] = datetime.utcnow()
        
        await db.get_collection("shutdownLogs").insert_one(shutdown_log)
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cannot shutdown: critical checklist items incomplete",
                "incompleteItems": validation_result["incompleteItems"]
            }
        )
    
    # Simulate shutdown process (2 second delay)
    await asyncio.sleep(2)
    
    # Update device status
    await db.get_collection("devices").update_one(
        {"deviceId": device_id}, 
        {"$set": {"status": "off", "lastShutdown": datetime.utcnow(), "updatedAt": datetime.utcnow()}}
    )
    
    # Create successful shutdown log
    shutdown_log = ShutdownCreate(
        device=device_id,
        user=current_user["sub"],
        userName=current_user["sub"],
        status="success",
        reason="Manual shutdown"
    ).dict()
    
    shutdown_log["logId"] = f"log-{datetime.utcnow().timestamp()}"
    shutdown_log["timestamp"] = datetime.utcnow()
    shutdown_log["duration"] = 2  # Simulated shutdown duration
    
    await db.get_collection("shutdownLogs").insert_one(shutdown_log)
    
    # Check if all devices are now powered off
    all_devices_cursor = db.get_collection("devices").find({})
    all_devices_off = True
    async for device in all_devices_cursor:
        if device.get("status", "on") == "on":
            all_devices_off = False
            break
    
    return {
        "status": "success",
        "message": f"Device {device_id} shutdown successfully",
        "allDevicesOff": all_devices_off
    }

@router.get("/status/{device_id}")
async def get_device_shutdown_status(device_id: str, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Get device status
    device = await db.get_collection("devices").find_one({"deviceId": device_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get last shutdown log for this device
    last_log = await db.get_collection("shutdownLogs").find_one(
        {"device": device_id}, 
        sort=[("timestamp", -1)]
    )
    
    status_info = {
        "deviceId": device_id,
        "deviceName": device.get("name", "Unknown"),
        "currentStatus": device.get("status", "on"),
        "lastShutdown": device.get("lastShutdown"),
        "lastShutdownStatus": last_log.get("status", "unknown") if last_log else "never"
    }
    
    if last_log:
        status_info["lastShutdownBy"] = last_log.get("userName", "Unknown")
        
    return status_info