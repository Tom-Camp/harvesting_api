from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.plant import Plant
from app.schemas.plant import PlantCreate, PlantUpdate


async def create_plant(session: AsyncSession, garden_id: int, data: PlantCreate) -> Plant:
    plant = Plant(garden_id=garden_id, **data.model_dump())
    session.add(plant)
    await session.commit()
    await session.refresh(plant)
    return plant


async def get_plants(session: AsyncSession, garden_id: int) -> list[Plant]:
    result = await session.execute(select(Plant).where(Plant.garden_id == garden_id))
    return list(result.scalars().all())


async def get_plant(session: AsyncSession, plant_id: int) -> Plant | None:
    return await session.get(Plant, plant_id)


async def update_plant(session: AsyncSession, plant: Plant, data: PlantUpdate) -> Plant:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(plant, key, value)
    session.add(plant)
    await session.commit()
    await session.refresh(plant)
    return plant


async def delete_plant(session: AsyncSession, plant: Plant) -> None:
    await session.delete(plant)
    await session.commit()
