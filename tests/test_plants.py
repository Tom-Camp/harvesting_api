import uuid

from httpx import AsyncClient

from app.models.garden import Garden
from app.models.plant import Plant
from app.models.user import User


async def test_list_plants_empty(client: AsyncClient, test_garden: Garden):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_plants(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["species"] == test_plant.species
    assert data[0]["variety"] == test_plant.variety


async def test_add_plant(client: AsyncClient, test_garden: Garden):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants",
        json={"plant_type": "vegetable", "species": "pepper", "variety": "bell"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["plant_type"] == "vegetable"
    assert data["species"] == "pepper"
    assert data["variety"] == "bell"
    assert data["notes"] == []


async def test_get_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["species"] == test_plant.species
    assert data["id"] == str(test_plant.id)


async def test_get_plant_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_update_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}",
        json={"variety": "roma"},
    )
    assert response.status_code == 200
    assert response.json()["variety"] == "roma"


async def test_delete_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.delete(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 404


async def test_plants_garden_not_found(client: AsyncClient):
    response = await client.get("/api/v1/gardens/no-such-garden/plants")
    assert response.status_code == 404


async def test_plants_require_active_account(pending_client: AsyncClient, test_garden: Garden):
    response = await pending_client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 403


async def test_member_can_add_plant(
    session, second_user: User, test_garden: Garden, second_client: AsyncClient
):
    from app.models.garden_member import GardenMember, GardenMemberRole
    session.add(GardenMember(garden_id=test_garden.id, user_id=second_user.id, role=GardenMemberRole.MEMBER))
    await session.commit()

    response = await second_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants",
        json={"plant_type": "herb", "species": "basil"},
    )
    assert response.status_code == 201
    assert response.json()["species"] == "basil"
