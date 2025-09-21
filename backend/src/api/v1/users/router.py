from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from datetime import datetime

from config.database import get_database
from src.models.user import UserResponse, UserCreate
from src.auth import get_current_user, require_role

router = APIRouter(prefix="", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    db = Depends(get_database), 
    current_user: Dict = Depends(require_role("Admin"))
):
    """Get all users - Admin only"""
    users = []
    async for user in db.get_collection("users").find():
        user_response = {
            "id": str(user["_id"]),
            "name": user["name"],
            "role": user["role"],
            "assignedDevices": user.get("assignedDevices", []),
            "createdAt": user["createdAt"].isoformat(),
            "updatedAt": user["updatedAt"].isoformat()
        }
        users.append(user_response)
    
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    db = Depends(get_database),
    current_user: Dict = Depends(require_role("Admin"))
):
    """Get user by ID - Admin only"""
    from bson import ObjectId
    try:
        user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "role": user["role"],
            "assignedDevices": user.get("assignedDevices", []),
            "createdAt": user["createdAt"].isoformat(),
            "updatedAt": user["updatedAt"].isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@router.put("/{user_id}/assign-devices")
async def assign_devices_to_user(
    user_id: str,
    device_ids: List[str],
    db = Depends(get_database),
    current_user: Dict = Depends(require_role("Admin"))
):
    """Assign devices to a user - Admin only"""
    from bson import ObjectId
    
    try:
        # Verify user exists
        user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify all devices exist
        for device_id in device_ids:
            device = await db.get_collection("devices").find_one({"deviceId": device_id})
            if not device:
                raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        
        # Update user's assigned devices
        result = await db.get_collection("users").update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "assignedDevices": device_ids,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update user")
        
        return {"message": f"Successfully assigned {len(device_ids)} devices to user"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid user ID or device assignment failed")

@router.put("/{user_id}/remove-devices")
async def remove_devices_from_user(
    user_id: str,
    device_ids: List[str],
    db = Depends(get_database),
    current_user: Dict = Depends(require_role("Admin"))
):
    """Remove devices from a user - Admin only"""
    from bson import ObjectId
    
    try:
        # Verify user exists
        user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get current assigned devices
        current_devices = user.get("assignedDevices", [])
        
        # Remove specified devices
        updated_devices = [device for device in current_devices if device not in device_ids]
        
        # Update user's assigned devices
        result = await db.get_collection("users").update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "assignedDevices": updated_devices,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to update user")
        
        # Also update devices collection to remove this user from assignedUsers
        user_name = user["name"]
        await db.get_collection("devices").update_many(
            {"deviceId": {"$in": device_ids}},
            {"$pull": {"assignedUsers": user_name}}
        )
        
        return {"message": f"Successfully removed {len(device_ids)} devices from user"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail="Invalid user ID or device removal failed")

@router.get("/engineers/with-devices")
async def get_engineers_with_devices(
    db = Depends(get_database),
    current_user: Dict = Depends(require_role("Admin"))
):
    """Get all engineers with their assigned devices - Admin only"""
    engineers = []
    async for user in db.get_collection("users").find({"role": "Engineer"}):
        # Get device details for assigned devices
        assigned_device_details = []
        for device_id in user.get("assignedDevices", []):
            device = await db.get_collection("devices").find_one({"deviceId": device_id})
            if device:
                assigned_device_details.append({
                    "deviceId": device["deviceId"],
                    "name": device["name"],
                    "status": device["status"],
                    "location": device.get("location")
                })
        
        engineer_info = {
            "id": str(user["_id"]),
            "name": user["name"],
            "role": user["role"],
            "assignedDevices": user.get("assignedDevices", []),
            "assignedDeviceDetails": assigned_device_details,
            "createdAt": user["createdAt"].isoformat(),
            "updatedAt": user["updatedAt"].isoformat()
        }
        engineers.append(engineer_info)
    
    return engineers