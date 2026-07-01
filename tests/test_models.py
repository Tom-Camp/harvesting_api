import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.garden import Garden
from app.models.plant import CareInfo, Note, NoteLabel, Plant, PlantType
from app.models.user import User, UserRole, UserStatus


# --- DB-level (before_insert / before_update events) ---


async def test_insert_strips_user_strings(session: AsyncSession):
    user = User(
        email="  trim@example.com  ",
        first_name="  Alice  ",
        last_name="\tSmith\n",
        status=UserStatus.ACTIVE,
        role=UserRole.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    assert user.email == "trim@example.com"
    assert user.first_name == "Alice"
    assert user.last_name == "Smith"


async def test_insert_strips_garden_strings(session: AsyncSession, test_user: User):
    garden = Garden(
        user_id=test_user.id,
        name="  My Garden  ",
        slug="my-garden",
        location="  Austin, TX  ",
        description="  some notes  ",
    )
    session.add(garden)
    await session.commit()
    await session.refresh(garden)
    assert garden.name == "My Garden"
    assert garden.location == "Austin, TX"
    assert garden.description == "some notes"


async def test_insert_strips_plant_strings(session: AsyncSession, test_garden: Garden):
    plant = Plant(
        garden_id=test_garden.id,
        plant_type=PlantType.VEGETABLE,
        species="  tomato  ",
        variety="  cherry  ",
    )
    session.add(plant)
    await session.commit()
    await session.refresh(plant)
    assert plant.species == "tomato"
    assert plant.variety == "cherry"


async def test_insert_strips_note_string(session: AsyncSession, test_plant: Plant):
    note = Note(plant_id=test_plant.id, note="  water weekly  ", label=NoteLabel.NOTE)
    session.add(note)
    await session.commit()
    await session.refresh(note)
    assert note.note == "water weekly"


async def test_insert_strips_care_info_strings(session: AsyncSession, test_plant: Plant):
    care = CareInfo(
        plant_id=test_plant.id,
        planting="  direct sow  ",
        care="\twater daily\t",
        harvesting="  pick when ripe  ",
        summary="  easy grower  ",
        latin_name="  Solanum lycopersicum  ",
    )
    session.add(care)
    await session.commit()
    await session.refresh(care)
    assert care.planting == "direct sow"
    assert care.care == "water daily"
    assert care.harvesting == "pick when ripe"
    assert care.summary == "easy grower"
    assert care.latin_name == "Solanum lycopersicum"


async def test_update_strips_strings(session: AsyncSession, test_garden: Garden):
    test_garden.name = "  Updated Name  "
    test_garden.location = "  Seattle, WA  "
    session.add(test_garden)
    await session.commit()
    await session.refresh(test_garden)
    assert test_garden.name == "Updated Name"
    assert test_garden.location == "Seattle, WA"


async def test_none_fields_unchanged(session: AsyncSession, test_garden: Garden):
    test_garden.description = None
    session.add(test_garden)
    await session.commit()
    await session.refresh(test_garden)
    assert test_garden.description is None


# --- API-level ---


async def test_create_garden_trims_whitespace(client: AsyncClient, test_user: User):
    response = await client.post(
        "/api/v1/gardens",
        json={"name": "  Veggie Patch  ", "location": "  Portland, OR  "},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Veggie Patch"
    assert data["location"] == "Portland, OR"


async def test_update_garden_trims_whitespace(client: AsyncClient, test_garden: Garden):
    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}",
        json={"name": "  Updated Name  ", "location": "  Seattle, WA  "},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["location"] == "Seattle, WA"
