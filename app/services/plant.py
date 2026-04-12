from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.plant import Harvest, Note, Plant, UnitType
from app.schemas.plant import HarvestCreate, HarvestUpdate, NoteCreate, NoteUpdate, PlantCreate, PlantUpdate


def _plant_query(plant_id: UUID | None = None):
    q = select(Plant).options(selectinload(Plant.notes), selectinload(Plant.harvests), selectinload(Plant.care_info))  # type: ignore[arg-type]
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


async def create_note(session: AsyncSession, plant_id: UUID, data: NoteCreate) -> Note:
    note = Note(plant_id=plant_id, **data.model_dump())
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def get_note(session: AsyncSession, note_id: UUID) -> Note | None:
    result = await session.execute(select(Note).where(Note.id == note_id))
    return result.scalar_one_or_none()


async def update_note(session: AsyncSession, note: Note, data: NoteUpdate) -> Note:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(note, key, value)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def delete_note(session: AsyncSession, note: Note) -> None:
    await session.delete(note)
    await session.commit()


async def create_harvest(session: AsyncSession, plant: Plant, data: HarvestCreate) -> Harvest:
    if plant.harvest_unit is None:
        plant.harvest_unit = data.unit
        session.add(plant)
    elif plant.harvest_unit != data.unit:
        raise ValueError(f"This plant's harvests are tracked in {plant.harvest_unit.value}")
    harvest = Harvest(plant_id=plant.id, **data.model_dump())
    session.add(harvest)
    await session.commit()
    await session.refresh(harvest)
    return harvest


async def get_harvest(session: AsyncSession, harvest_id: UUID) -> Harvest | None:
    result = await session.execute(select(Harvest).where(Harvest.id == harvest_id))
    return result.scalar_one_or_none()


async def update_harvest(session: AsyncSession, harvest: Harvest, data: HarvestUpdate) -> Harvest:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(harvest, key, value)
    session.add(harvest)
    await session.commit()
    await session.refresh(harvest)
    return harvest


async def delete_harvest(session: AsyncSession, harvest: Harvest) -> None:
    await session.delete(harvest)
    await session.commit()
