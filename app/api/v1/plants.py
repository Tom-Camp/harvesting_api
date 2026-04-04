from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.garden_advisor import get_plant_tips
from app.db import get_session
from app.models.garden import Garden
from app.models.user import User
from app.schemas.ai import GardenTipsResponse, TipMode
from app.schemas.plant import PlantCreate, PlantRead, PlantUpdate
from app.services import garden as garden_service
from app.services import plant as plant_service
from app.services import user as user_service

router = APIRouter(prefix="/garden/plants", tags=["plants"])


async def _resolve_user_garden(
    session: AsyncSession,
    user_id: int,
) -> tuple[User, Garden]:
    user = await user_service.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    garden = await garden_service.get_garden_by_user(session, user_id)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    return user, garden


@router.get("", response_model=list[PlantRead])
async def list_plants(
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> list[PlantRead]:
    _, garden = await _resolve_user_garden(session, user_id)
    plants = await plant_service.get_plants(session, garden.id)
    return [PlantRead.model_validate(p) for p in plants]


@router.post("", response_model=PlantRead, status_code=status.HTTP_201_CREATED)
async def add_plant(
    data: PlantCreate,
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    _, garden = await _resolve_user_garden(session, user_id)
    plant = await plant_service.create_plant(session, garden.id, data)
    return PlantRead.model_validate(plant)


@router.get("/{plant_id}", response_model=PlantRead)
async def get_plant(
    plant_id: int,
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    _, garden = await _resolve_user_garden(session, user_id)
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return PlantRead.model_validate(plant)


@router.patch("/{plant_id}", response_model=PlantRead)
async def update_plant(
    plant_id: int,
    data: PlantUpdate,
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    _, garden = await _resolve_user_garden(session, user_id)
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    plant = await plant_service.update_plant(session, plant, data)
    return PlantRead.model_validate(plant)


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: int,
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> None:
    _, garden = await _resolve_user_garden(session, user_id)
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    await plant_service.delete_plant(session, plant)


@router.post("/{plant_id}/tips", response_model=GardenTipsResponse)
async def get_tips(
    plant_id: int,
    mode: TipMode,
    user_id: int = Query(...),  # TODO: replace with auth dependency
    session: AsyncSession = Depends(get_session),
) -> GardenTipsResponse:
    user, garden = await _resolve_user_garden(session, user_id)
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return await get_plant_tips(
        plant_type=plant.plant_type,
        mode=mode,
        variety=plant.variety,
        location=user.location,
    )
