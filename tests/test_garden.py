from httpx import AsyncClient

from app.models.garden import Garden
from app.models.user import User


async def test_create_garden(client: AsyncClient, test_user: User):
    response = await client.post("/api/v1/garden", json={"name": "Veggie Patch"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Veggie Patch"
    assert data["user_id"] == str(test_user.id)


async def test_create_garden_conflict(client: AsyncClient, test_garden: Garden):
    response = await client.post("/api/v1/garden", json={"name": "Second Garden"})
    assert response.status_code == 409


async def test_get_garden(client: AsyncClient, test_garden: Garden):
    response = await client.get("/api/v1/garden")
    assert response.status_code == 200
    assert response.json()["name"] == test_garden.name


async def test_get_garden_not_found(client: AsyncClient, test_user: User):
    response = await client.get("/api/v1/garden")
    assert response.status_code == 404


async def test_update_garden(client: AsyncClient, test_garden: Garden):
    response = await client.patch("/api/v1/garden", json={"name": "Updated Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


async def test_update_garden_not_found(client: AsyncClient, test_user: User):
    response = await client.patch("/api/v1/garden", json={"name": "Won't Work"})
    assert response.status_code == 404


async def test_garden_requires_complete_profile(incomplete_client: AsyncClient):
    response = await incomplete_client.get("/api/v1/garden")
    assert response.status_code == 403
