from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.garden import Garden
from app.schemas.garden import GardenCreate, GardenUpdate


async def create_garden(session: AsyncSession, user_id: int, data: GardenCreate) -> Garden:
    garden = Garden(user_id=user_id, name=data.name)
    session.add(garden)
    await session.commit()
    await session.refresh(garden)
    return garden


async def get_garden_by_user(session: AsyncSession, user_id: int) -> Garden | None:
    result = await session.execute(select(Garden).where(Garden.user_id == user_id))
    return result.scalar_one_or_none()


async def update_garden(session: AsyncSession, garden: Garden, data: GardenUpdate) -> Garden:
    garden.name = data.name
    session.add(garden)
    await session.commit()
    await session.refresh(garden)
    return garden
