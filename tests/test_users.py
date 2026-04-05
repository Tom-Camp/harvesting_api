from httpx import AsyncClient

from app.models.user import User


async def test_get_me(client: AsyncClient, test_user: User):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["location"] == test_user.location
    assert data["first_name"] == test_user.first_name
    assert "id" in data


async def test_update_me_location(client: AsyncClient):
    response = await client.patch("/api/v1/users/me", json={"location": "Portland, OR"})
    assert response.status_code == 200
    assert response.json()["location"] == "Portland, OR"


async def test_get_me_unauthenticated(unauthed_client: AsyncClient):
    response = await unauthed_client.get("/api/v1/users/me")
    assert response.status_code == 401
