import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.garden_advisor import get_plant_tips
from app.auth.dependencies import GardenAccess, require_garden_member
from app.db import get_session
from app.models.plant import CareInfo
from app.schemas.plant import CareInfoRead, PlantCreate, PlantRead, PlantUpdate
from app.services import plant as plant_service

router = APIRouter(prefix="/gardens/{slug}/plants", tags=["plants"])


@router.get("", response_model=list[PlantRead])
async def list_plants(
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> list[PlantRead]:
    plants = await plant_service.get_plants(session=session, garden_id=access.garden.id)
    return [PlantRead.model_validate(p) for p in plants]


@router.post("", response_model=PlantRead, status_code=status.HTTP_201_CREATED)
async def add_plant(
    data: PlantCreate,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    plant = await plant_service.create_plant(session=session, garden_id=access.garden.id, data=data)
    return PlantRead.model_validate(plant)


@router.get("/{plant_id}", response_model=PlantRead)
async def get_plant(
    plant_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return PlantRead.model_validate(plant)


@router.patch("/{plant_id}", response_model=PlantRead)
async def update_plant(
    plant_id: uuid.UUID,
    data: PlantUpdate,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    plant = await plant_service.update_plant(session, plant, data)
    return PlantRead.model_validate(plant)


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> None:
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    await plant_service.delete_plant(session, plant)


@router.post("/{plant_id}/care", response_model=CareInfoRead)
async def get_care_info(
    plant_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> CareInfo:
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return await get_plant_tips(
        plant_type=plant.plant_type,
        variety=plant.variety,
        location=access.garden.location,
    )
