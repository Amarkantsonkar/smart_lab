from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from config.database import get_database
from src.models.checklist import ChecklistCreate, ChecklistUpdate, ChecklistResponse
from src.auth import get_current_user, require_role

router = APIRouter(prefix="", tags=["checklist"])

@router.post("/", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist_item(item: ChecklistCreate, db = Depends(get_database), current_user: dict = Depends(require_role("Admin"))):
    # Check if item with same taskId already exists
    existing_item = await db.get_collection("checklist").find_one({"taskId": item.taskId})
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Checklist item with this ID already exists"
        )
    
    # Create item document
    item_dict = item.dict()
    
    # Insert item into database
    result = await db.get_collection("checklist").insert_one(item_dict)
    created_item = await db.get_collection("checklist").find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string for JSON serialization
    created_item["id"] = str(created_item.pop("_id"))
    created_item["createdAt"] = created_item["createdAt"].isoformat()
    created_item["updatedAt"] = created_item["updatedAt"].isoformat()
    
    return created_item

@router.get("/", response_model=List[ChecklistResponse])
async def read_checklist_items(skip: int = 0, limit: int = 100, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    items_cursor = db.get_collection("checklist").find().skip(skip).limit(limit)
    items = []
    async for item in items_cursor:
        item["id"] = str(item.pop("_id"))
        item["createdAt"] = item["createdAt"].isoformat()
        item["updatedAt"] = item["updatedAt"].isoformat()
        items.append(item)
    
    return items

@router.get("/{task_id}", response_model=ChecklistResponse)
async def read_checklist_item(task_id: str, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    item = await db.get_collection("checklist").find_one({"taskId": task_id})
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    item["id"] = str(item.pop("_id"))
    item["createdAt"] = item["createdAt"].isoformat()
    item["updatedAt"] = item["updatedAt"].isoformat()
    
    return item

@router.put("/{task_id}", response_model=ChecklistResponse)
async def update_checklist_item(task_id: str, item_update: ChecklistUpdate, db = Depends(get_database), current_user: dict = Depends(get_current_user)):
    # Get existing item
    existing_item = await db.get_collection("checklist").find_one({"taskId": task_id})
    if not existing_item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    # Prepare update data
    update_data = item_update.dict(exclude_unset=True)
    if update_data:
        update_data["updatedAt"] = datetime.utcnow()
        
        # If completed status is being updated
        if "completed" in update_data and update_data["completed"]:
            update_data["completedBy"] = current_user["sub"]
            update_data["completedAt"] = datetime.utcnow()
        
        # Update item in database
        await db.get_collection("checklist").update_one(
            {"taskId": task_id}, {"$set": update_data}
        )
    
    # Get updated item
    updated_item = await db.get_collection("checklist").find_one({"taskId": task_id})
    updated_item["id"] = str(updated_item.pop("_id"))
    updated_item["createdAt"] = updated_item["createdAt"].isoformat()
    updated_item["updatedAt"] = updated_item["updatedAt"].isoformat()
    
    return updated_item

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item(task_id: str, db = Depends(get_database), current_user: dict = Depends(require_role("Admin"))):
    # Check if item exists
    existing_item = await db.get_collection("checklist").find_one({"taskId": task_id})
    if not existing_item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    # Delete item
    await db.get_collection("checklist").delete_one({"taskId": task_id})
    
    return None