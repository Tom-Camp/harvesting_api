from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas.garden import GardenCreate, GardenRead, GardenUpdate
from app.services import garden as garden_service
from app.services import user as user_service

router = APIRouter(prefix="/garden", tags=["garden"])


@router.post("", response_model=GardenRead, status_code=status.HTTP_201_CREATED)
async def create_garden(
    data: GardenCreate,
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> GardenRead:
    user = await user_service.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    existing = await garden_service.get_garden_by_user(session, user_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Garden already exists")
    garden = await garden_service.create_garden(session, user_id, data)
    return GardenRead.model_validate(garden)


@router.get("", response_model=GardenRead)
async def get_garden(
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> GardenRead:
    garden = await garden_service.get_garden_by_user(session, user_id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    return GardenRead.model_validate(garden)


@router.patch("", response_model=GardenRead)
async def update_garden(
    data: GardenUpdate,
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> GardenRead:
    garden = await garden_service.get_garden_by_user(session, user_id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    garden = await garden_service.update_garden(session, garden, data)
    return GardenRead.model_validate(garden)
