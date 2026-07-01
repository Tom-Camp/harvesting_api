from uuid import UUID

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.garden import Garden, GardenNote
from app.models.garden_member import GardenMember, GardenMemberRole
from app.schemas.garden import GardenCreate, GardenNoteCreate, GardenNoteUpdate, GardenUpdate


def _garden_query(garden_id: UUID | None = None):
    q = select(Garden).options(selectinload(Garden.notes))  # type: ignore[arg-type]
    if garden_id is not None:
        q = q.where(Garden.id == garden_id)
    return q


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
    garden = Garden(user_id=user_id, name=data.name, slug=slug, location=data.location, description=data.description)
    session.add(garden)
    await session.flush()
    session.add(GardenMember(garden_id=garden.id, user_id=user_id, role=GardenMemberRole.OWNER))
    await session.commit()
    result = await session.execute(_garden_query(garden.id))
    return result.scalar_one()


async def get_garden_by_slug(session: AsyncSession, slug: str) -> Garden | None:
    result = await session.execute(_garden_query().where(Garden.slug == slug))
    return result.scalar_one_or_none()


async def get_accessible_gardens(session: AsyncSession, user_id: UUID) -> list[Garden]:
    result = await session.execute(
        _garden_query()
        .join(GardenMember, GardenMember.garden_id == Garden.id)
        .where(GardenMember.user_id == user_id)
    )
    return list(result.scalars().all())


async def update_garden(session: AsyncSession, garden: Garden, data: GardenUpdate) -> Garden:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(garden, key, value)
    session.add(garden)
    await session.commit()
    result = await session.execute(_garden_query(garden.id))
    return result.scalar_one()


async def list_all_gardens(session: AsyncSession) -> list[Garden]:
    result = await session.execute(_garden_query())
    return list(result.scalars().all())


async def delete_garden(session: AsyncSession, garden: Garden) -> None:
    await session.delete(garden)
    await session.commit()


async def create_garden_note(session: AsyncSession, garden_id: UUID, data: GardenNoteCreate) -> GardenNote:
    note = GardenNote(garden_id=garden_id, **data.model_dump())
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def get_garden_note(session: AsyncSession, note_id: UUID) -> GardenNote | None:
    result = await session.execute(select(GardenNote).where(GardenNote.id == note_id))
    return result.scalar_one_or_none()


async def update_garden_note(session: AsyncSession, note: GardenNote, data: GardenNoteUpdate) -> GardenNote:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(note, key, value)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def delete_garden_note(session: AsyncSession, note: GardenNote) -> None:
    await session.delete(note)
    await session.commit()
