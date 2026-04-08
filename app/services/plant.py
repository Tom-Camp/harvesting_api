from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.plant import Plant
from app.schemas.plant import PlantCreate, PlantUpdate


def _plant_query(plant_id: UUID | None = None):
    q = select(Plant).options(selectinload(Plant.notes), selectinload(Plant.care_info))  # type: ignore[arg-type]
    if plant_id is not None:
        q = q.where(Plant.id == plant_id)
    return q


async def create_plant(session: AsyncSession, garden_id: UUID, data: PlantCreate) -> Plant:
    plant = Plant(garden_id=garden_id, **data.model_dump())
    session.add(plant)
    await session.commit()
    result = await session.execute(_plant_query(plant.id))
    return result.scalar_one()


async def get_plants(session: AsyncSession, garden_id: UUID) -> list[Plant]:
    result = await session.execute(_plant_query().where(Plant.garden_id == garden_id))
    return list(result.scalars().all())


async def get_plant(session: AsyncSession, plant_id: UUID) -> Plant | None:
    result = await session.execute(_plant_query(plant_id))
    return result.scalar_one_or_none()


async def update_plant(session: AsyncSession, plant: Plant, data: PlantUpdate) -> Plant:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(plant, key, value)
    session.add(plant)
    await session.commit()
    result = await session.execute(_plant_query(plant.id))
    return result.scalar_one()


async def delete_plant(session: AsyncSession, plant: Plant) -> None:
    await session.delete(plant)
    await session.commit()
