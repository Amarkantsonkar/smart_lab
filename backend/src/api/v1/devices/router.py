from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import asyncio

from config.database import get_database
from src.models.device import DeviceCreate, DeviceUpdate, DeviceResponse
from src.auth import get_current_user, require_role

router = APIRouter(prefix="", tags=["devices"])

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate, db = Depends(get_database), current_user: dict = Depends(require_role("Admin"))):
    # Check if device with same deviceId already exists
    existing_device = await db.get_collection("devices").find_one({"deviceId": device.deviceId})
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this ID already exists"
        )
    
    # Create device document
    device_dict = device.dict()
    
    # Insert device into database
    result = await db.get_collection("devices").insert_one(device_dict)
    created_device = await db.get_collection("devices").find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string for JSON serialization
    created_device["id"] = str(created_device.pop("_id"))
    created_device["createdAt"] = created_device["createdAt"].isoformat()
    created_device["updatedAt"] = created_device["updatedAt"].isoformat()
    if created_device.get("lastShutdown"):
        created_device["lastShutdown"] = created_device["lastShutdown"].isoformat()
    if created_device.get("lastStartup"):
        created_device["lastStartup"] = created_device["lastStartup"].isoformat()
    
    return created_device

@router.get("/", response_model=List[DeviceResponse])
async def read_devices(skip: int = 0, limit: int = 100, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    devices_cursor = db.get_collection("devices").find().skip(skip).limit(limit)
    devices = []
    async for device in devices_cursor:
        device["id"] = str(device.pop("_id"))
        device["createdAt"] = device["createdAt"].isoformat()
        device["updatedAt"] = device["updatedAt"].isoformat()
        if device.get("lastShutdown"):
            device["lastShutdown"] = device["lastShutdown"].isoformat()
        if device.get("lastStartup"):
            device["lastStartup"] = device["lastStartup"].isoformat()
        devices.append(device)
    
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
async def read_device(device_id: str, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    device = await db.get_collection("devices").find_one({"deviceId": device_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device["id"] = str(device.pop("_id"))
    device["createdAt"] = device["createdAt"].isoformat()
    device["updatedAt"] = device["updatedAt"].isoformat()
    if device.get("lastShutdown"):
        device["lastShutdown"] = device["lastShutdown"].isoformat()
    if device.get("lastStartup"):
        device["lastStartup"] = device["lastStartup"].isoformat()
    
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: str, device_update: DeviceUpdate, db = Depends(get_database), current_user: dict = Depends(require_role("Admin"))):
    # Get existing device
    existing_device = await db.get_collection("devices").find_one({"deviceId": device_id})
    if not existing_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Prepare update data
    update_data = device_update.dict(exclude_unset=True)
    if update_data:
        update_data["updatedAt"] = datetime.utcnow()
        
        # Update device in database
        await db.get_collection("devices").update_one(
            {"deviceId": device_id}, {"$set": update_data}
        )
    
    # Get updated device
    updated_device = await db.get_collection("devices").find_one({"deviceId": device_id})
    updated_device["id"] = str(updated_device.pop("_id"))
    updated_device["createdAt"] = updated_device["createdAt"].isoformat()
    updated_device["updatedAt"] = updated_device["updatedAt"].isoformat()
    if updated_device.get("lastShutdown"):
        updated_device["lastShutdown"] = updated_device["lastShutdown"].isoformat()
    if updated_device.get("lastStartup"):
        updated_device["lastStartup"] = updated_device["lastStartup"].isoformat()
    
    return updated_device

@router.post("/start/{device_id}")
async def start_device(device_id: str, db = Depends(get_database), current_user: dict = Depends(require_role("Admin"))):
    """Start/power on a device. Admin only."""
    # Get existing device
    existing_device = await db.get_collection("devices").find_one({"deviceId": device_id})
    if not existing_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check if device is already on
    if existing_device.get("status") == "on":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device is already powered on"
        )
    
    # Simulate startup process (3 second delay)
    await asyncio.sleep(3)
    
    # Update device status to "on"
    await db.get_collection("devices").update_one(
        {"deviceId": device_id}, 
        {"$set": {"status": "on", "lastStartup": datetime.utcnow(), "updatedAt": datetime.utcnow()}}
    )
    
    return {
        "status": "success",
        "message": f"Device {device_id} started successfully",
        "deviceId": device_id,
        "newStatus": "on"
    }

@router.post("/start-all")
async def start_all_devices(db = Depends(get_database), current_user: dict = Depends(require_role("Admin"))):
    """Start all devices that are currently off. Admin only."""
    # Get all devices that are off or in maintenance
    off_devices_cursor = db.get_collection("devices").find({"status": {"$in": ["off", "maintenance"]}})
    off_devices = []
    async for device in off_devices_cursor:
        off_devices.append(device)
    
    if not off_devices:
        return {
            "status": "info",
            "message": "All devices are already powered on",
            "devicesStarted": 0
        }
    
    # Simulate startup process for all devices (5 second delay)
    await asyncio.sleep(5)
    
    # Update all off devices to "on" status
    device_ids = [device["deviceId"] for device in off_devices]
    await db.get_collection("devices").update_many(
        {"deviceId": {"$in": device_ids}},
        {"$set": {"status": "on", "lastStartup": datetime.utcnow(), "updatedAt": datetime.utcnow()}}
    )
    
    return {
        "status": "success",
        "message": f"Successfully started {len(off_devices)} devices",
        "devicesStarted": len(off_devices),
        "startedDevices": device_ids
    }

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: str, db = Depends(get_database), current_user: dict = Depends(require_role("Admin"))):
    # Check if device exists
    existing_device = await db.get_collection("devices").find_one({"deviceId": device_id})
    if not existing_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Delete device
    await db.get_collection("devices").delete_one({"deviceId": device_id})
    
    return None