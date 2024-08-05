from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List
from services.group_services import GroupServices


router = APIRouter()

class GroupRequest(BaseModel):
    name: str
    description: str = None
    events: List[str] = []

class DeleteGroupRequest(BaseModel):
    name: str

class GroupDetailRequest(BaseModel):
    name: str

def get_groups_helper(request: Request):
    return GroupServices(request.app.state.DB_HELPER, request.app.state.LOGGER)


@router.get("/api/get_groups")
async def get_groups(group_helper: GroupServices = Depends(get_groups_helper)):

    try:
        groups = group_helper.get_all_groups()
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/save_group")
async def save_group(request: GroupRequest, group_helper: GroupServices = Depends(get_groups_helper)):
    try:
        group_name = request.name
        description = request.description
        events = request.events

        if not group_name or not events:
            raise HTTPException(status_code=400, detail="Group name and events are required")

        group_helper.save_group(group_name, events, description)

        return {"message": "Group saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/delete_group")
async def delete_group(request: DeleteGroupRequest, group_helper: GroupServices = Depends(get_groups_helper)):
    try:
        group_name = request.name

        if not group_name:
            raise HTTPException(status_code=400, detail="Group name is required")

        group_helper.delete_group(group_name)

        return {"message": "Group deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/get_group_details")
async def get_group_details(request: GroupDetailRequest, group_helper: GroupServices = Depends(get_groups_helper)):
    try:
        group_name = request.name

        if not group_name:
            raise HTTPException(status_code=400, detail="Group name is required")

        group = group_helper.get_group_details(group_name)

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        return group
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
