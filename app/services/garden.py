from uuid import UUID

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.garden import Garden
from app.models.garden_member import GardenMember, GardenMemberRole
from app.schemas.garden import GardenCreate, GardenUpdate


async def _generate_unique_slug(session: AsyncSession, name: str) -> str:
    base = slugify(name)
    slug = base
    n = 2
    while True:
        result = await session.execute(select(Garden).where(Garden.slug == slug))
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base}-{n}"
        n += 1


async def create_garden(session: AsyncSession, user_id: UUID, data: GardenCreate) -> Garden:
    slug = await _generate_unique_slug(session, data.name)
    garden = Garden(user_id=user_id, name=data.name, slug=slug, location=data.location, notes=data.notes)
    session.add(garden)
    await session.flush()
    session.add(GardenMember(garden_id=garden.id, user_id=user_id, role=GardenMemberRole.OWNER))
    await session.commit()
    await session.refresh(garden)
    return garden


async def get_garden_by_slug(session: AsyncSession, slug: str) -> Garden | None:
    result = await session.execute(select(Garden).where(Garden.slug == slug))
    return result.scalar_one_or_none()


async def get_accessible_gardens(session: AsyncSession, user_id: UUID) -> list[Garden]:
    result = await session.execute(
        select(Garden)
        .join(GardenMember, GardenMember.garden_id == Garden.id)
        .where(GardenMember.user_id == user_id)
    )
    return list(result.scalars().all())


async def update_garden(session: AsyncSession, garden: Garden, data: GardenUpdate) -> Garden:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(garden, key, value)
    session.add(garden)
    await session.commit()
    await session.refresh(garden)
    return garden


async def list_all_gardens(session: AsyncSession) -> list[Garden]:
    result = await session.execute(select(Garden))
    return list(result.scalars().all())


async def delete_garden(session: AsyncSession, garden: Garden) -> None:
    await session.delete(garden)
    await session.commit()
