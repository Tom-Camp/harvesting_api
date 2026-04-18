import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import GardenAccess, require_garden_member
from app.db import get_session
from app.schemas.plant import HarvestCreate, HarvestRead, HarvestUpdate
from app.services import plant as plant_service

router = APIRouter(prefix="/gardens/{slug}/plants/{plant_id}/harvests", tags=["harvests"])


async def _get_plant_in_garden(
    plant_id: uuid.UUID,
    access: GardenAccess,
    session: AsyncSession,
):
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


@router.post("", response_model=HarvestRead, status_code=status.HTTP_201_CREATED)
async def add_harvest(
    plant_id: uuid.UUID,
    data: HarvestCreate,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> HarvestRead:
    plant = await _get_plant_in_garden(plant_id, access, session)
    try:
        harvest = await plant_service.create_harvest(session=session, plant=plant, data=data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return HarvestRead.model_validate(harvest)


@router.patch("/{harvest_id}", response_model=HarvestRead)
async def update_harvest(
    plant_id: uuid.UUID,
    harvest_id: uuid.UUID,
    data: HarvestUpdate,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> HarvestRead:
    plant = await _get_plant_in_garden(plant_id, access, session)
    harvest = await plant_service.get_harvest(session, harvest_id)
    if not harvest or harvest.plant_id != plant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Harvest not found")
    if plant.harvest_unit and data.unit != plant.harvest_unit:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"This plant's harvests are tracked in {plant.harvest_unit.value}",
        )
    harvest = await plant_service.update_harvest(session, harvest, data)
    return HarvestRead.model_validate(harvest)


@router.delete("/{harvest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_harvest(
    plant_id: uuid.UUID,
    harvest_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> None:
    await _get_plant_in_garden(plant_id, access, session)
    harvest = await plant_service.get_harvest(session, harvest_id)
    if not harvest or harvest.plant_id != plant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Harvest not found")
    await plant_service.delete_harvest(session, harvest)
