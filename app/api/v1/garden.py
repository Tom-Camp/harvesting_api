from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_complete_profile
from app.db import get_session
from app.models.user import User
from app.schemas.garden import GardenCreate, GardenRead, GardenUpdate
from app.services import garden as garden_service

router = APIRouter(prefix="/garden", tags=["garden"])


@router.post("", response_model=GardenRead, status_code=status.HTTP_201_CREATED)
async def create_garden(
    data: GardenCreate,
    user: User = Depends(require_complete_profile),
    session: AsyncSession = Depends(get_session),
) -> GardenRead:
    existing = await garden_service.get_garden_by_user(session, user.id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Garden already exists")
    garden = await garden_service.create_garden(session, user.id, data)
    return GardenRead.model_validate(garden)


@router.get("", response_model=GardenRead)
async def get_garden(
    user: User = Depends(require_complete_profile),
    session: AsyncSession = Depends(get_session),
) -> GardenRead:
    garden = await garden_service.get_garden_by_user(session, user.id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    return GardenRead.model_validate(garden)


@router.patch("", response_model=GardenRead)
async def update_garden(
    data: GardenUpdate,
    user: User = Depends(require_complete_profile),
    session: AsyncSession = Depends(get_session),
) -> GardenRead:
    garden = await garden_service.get_garden_by_user(session, user.id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    garden = await garden_service.update_garden(session, garden, data)
    return GardenRead.model_validate(garden)
