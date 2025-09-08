from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.utils import get_current_active_profile
from src.core.exceptions import NotFoundException
from src.database import get_db
from src.profile.schemas import ProfileCreateSchema, ProfileResponse, ProfileListResponse
from src.profile.service import ProfileService

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(dependencies=[Depends(get_current_active_profile)])


@router.get("/profile-list/{profile_id}", response_model=ProfileListResponse)
async def get_profile_list(profile_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    auth_service: ProfileService = ProfileService(db)
    profile = await auth_service.find_all(filters={"id": profile_id})
    if not profile:
        raise NotFoundException("Profile not found")
    return ProfileListResponse(data=profile)


@router.get("/profile/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    auth_service: ProfileService = ProfileService(db)
    profile = await auth_service.get_one(profile_id)
    if not profile:
        raise NotFoundException("Profile not found")
    return ProfileResponse(data=profile)


@router.post("/profile", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreateSchema,
    db: Annotated[AsyncSession, Depends(get_db)]):
    auth_service: ProfileService = ProfileService(db)
    new_profile = await auth_service.add_one(profile_data.model_dump())
    print("PROFILE ID", new_profile.id)
    return ProfileResponse(data=new_profile)


@router.put("/profile/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int, profile_data: ProfileCreateSchema,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    auth_service: ProfileService = ProfileService(db)
    data = profile_data.model_dump()
    updated_profile = await auth_service.update_one(profile_id, data)
    if not updated_profile:
        raise NotFoundException("Profile not found")
    return ProfileResponse(data=updated_profile)


@router.delete("/profile/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    auth_service: ProfileService = ProfileService(db)
    deleted = await auth_service.delete_one(profile_id)
    if not deleted:
        raise NotFoundException("Profile not found")
    return
