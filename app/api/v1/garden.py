from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import GardenAccess, require_active_user, require_garden_member, require_garden_owner
from app.db import get_session
from app.models.user import User
from app.schemas.garden import GardenCreate, GardenRead, GardenUpdate
from app.services import garden as garden_service

router = APIRouter(prefix="/gardens", tags=["gardens"])


@router.post("", response_model=GardenRead, status_code=status.HTTP_201_CREATED)
async def create_garden(
    data: GardenCreate,
    user: User = Depends(require_active_user),
    session: AsyncSession = Depends(get_session),
) -> GardenRead:
    garden = await garden_service.create_garden(session, user.id, data)
    return GardenRead.model_validate(garden)


@router.get("", response_model=list[GardenRead])
async def list_gardens(
    user: User = Depends(require_active_user),
    session: AsyncSession = Depends(get_session),
) -> list[GardenRead]:
    gardens = await garden_service.get_accessible_gardens(session, user.id)
    return [GardenRead.model_validate(g) for g in gardens]


@router.get("/{slug}", response_model=GardenRead)
async def get_garden(access: GardenAccess = Depends(require_garden_member)) -> GardenRead:
    return GardenRead.model_validate(access.garden)


@router.patch("/{slug}", response_model=GardenRead)
async def update_garden(
    data: GardenUpdate,
    access: GardenAccess = Depends(require_garden_owner),
    session: AsyncSession = Depends(get_session),
) -> GardenRead:
    garden = await garden_service.update_garden(session, access.garden, data)
    return GardenRead.model_validate(garden)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_garden(
    access: GardenAccess = Depends(require_garden_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    await garden_service.delete_garden(session, access.garden)
