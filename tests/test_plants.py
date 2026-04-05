import uuid

from httpx import AsyncClient

from app.models.garden import Garden
from app.models.plant import Plant
from app.models.user import User


async def test_list_plants_empty(client: AsyncClient, test_garden: Garden):
    response = await client.get("/api/v1/garden/plants")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_plants(client: AsyncClient, test_plant: Plant):
    response = await client.get("/api/v1/garden/plants")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["plant_type"] == test_plant.plant_type
    assert data[0]["variety"] == test_plant.variety


async def test_add_plant(client: AsyncClient, test_garden: Garden):
    response = await client.post(
        "/api/v1/garden/plants",
        json={"plant_type": "pepper", "variety": "bell"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["plant_type"] == "pepper"
    assert data["variety"] == "bell"
    assert data["notes"] is None


async def test_get_plant(client: AsyncClient, test_plant: Plant):
    response = await client.get(f"/api/v1/garden/plants/{test_plant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["plant_type"] == test_plant.plant_type
    assert data["id"] == str(test_plant.id)


async def test_get_plant_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.get(f"/api/v1/garden/plants/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_update_plant(client: AsyncClient, test_plant: Plant):
    response = await client.patch(
        f"/api/v1/garden/plants/{test_plant.id}",
        json={"variety": "roma", "notes": "staked to trellis"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["variety"] == "roma"
    assert data["notes"] == "staked to trellis"


async def test_delete_plant(client: AsyncClient, test_plant: Plant):
    response = await client.delete(f"/api/v1/garden/plants/{test_plant.id}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/garden/plants/{test_plant.id}")
    assert response.status_code == 404


async def test_plants_requires_garden(client: AsyncClient, test_user: User):
    """No garden created for this user — should 404 before reaching plant logic."""
    response = await client.get("/api/v1/garden/plants")
    assert response.status_code == 404


async def test_plants_require_complete_profile(incomplete_client: AsyncClient):
    response = await incomplete_client.get("/api/v1/garden/plants")
    assert response.status_code == 403
