import logging
import uuid

from asyncpg import PostgresError
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic_ai.exceptions import AgentRunError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.garden_advisor import get_latin_name, get_plant_tips
from app.auth.dependencies import GardenAccess, require_garden_member, require_garden_owner
from app.db import _SessionLocal, get_session
from app.models.plant import CareInfo
from app.schemas.plant import CareInfoRead, PlantCreate, PlantRead, PlantUpdate
from app.services import plant as plant_service

logger = logging.getLogger(__name__)


async def _populate_latin_name(plant_id: uuid.UUID, plant_type: str, species: str, variety: str | None) -> None:
    try:
        latin_name = await get_latin_name(plant_type=plant_type, species=species, variety=variety)
        async with _SessionLocal() as session:
            plant = await plant_service.get_plant(session, plant_id)
            if plant and latin_name:
                plant.latin_name = latin_name
                session.add(plant)
                await session.commit()
    except (AgentRunError, SQLAlchemyError, PostgresError):
        logger.exception("Failed to populate latin_name for plant %s", plant_id)

router = APIRouter(prefix="/gardens/{slug}/plants", tags=["plants"])


@router.get("", response_model=list[PlantRead])
async def list_plants(
    archived: bool = False,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> list[PlantRead]:
    plants = await plant_service.get_plants(session=session, garden_id=access.garden.id, archived=archived)
    return [PlantRead.model_validate(p) for p in plants]


@router.post("", response_model=PlantRead, status_code=status.HTTP_201_CREATED)
async def add_plant(
    data: PlantCreate,
    background_tasks: BackgroundTasks,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    plant = await plant_service.create_plant(session=session, garden_id=access.garden.id, data=data)
    background_tasks.add_task(_populate_latin_name, plant.id, plant.plant_type, plant.species, plant.variety)
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
    access: GardenAccess = Depends(require_garden_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    await plant_service.delete_plant(session, plant)


@router.post("/{plant_id}/archive", response_model=PlantRead)
async def archive_plant(
    plant_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    plant = await plant_service.archive_plant(session, plant)
    return PlantRead.model_validate(plant)


@router.post("/{plant_id}/unarchive", response_model=PlantRead)
async def unarchive_plant(
    plant_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> PlantRead:
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    plant = await plant_service.unarchive_plant(session, plant)
    return PlantRead.model_validate(plant)


@router.post("/{plant_id}/care", response_model=CareInfoRead)
async def get_care_info(
    plant_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> CareInfo:
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")

    if plant.care_info:
        await session.delete(plant.care_info)
        await session.flush()

    tips = await get_plant_tips(
        plant_type=plant.plant_type,
        species=plant.species,
        variety=plant.variety,
        location=access.garden.location,
    )
    care_info = CareInfo(
        planting=tips.planting,
        care=tips.care,
        harvesting=tips.harvesting,
        summary=tips.summary,
        latin_name=tips.latin_name,
        plant_id=plant.id,
    )
    session.add(care_info)
    await session.commit()
    await session.refresh(care_info)
    return care_info
