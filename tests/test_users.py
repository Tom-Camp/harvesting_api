from httpx import AsyncClient

from app.models.user import User


async def test_get_me(client: AsyncClient, test_user: User):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["status"] == "active"
    assert data["role"] == "user"
    assert data["first_name"] == test_user.first_name


async def test_update_me(client: AsyncClient):
    response = await client.patch("/api/v1/users/me", json={"first_name": "Updated"})
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


async def test_get_me_unauthenticated(unauthed_client: AsyncClient):
    response = await unauthed_client.get("/api/v1/users/me")
    assert response.status_code == 401  # HTTPBearer returns 401 when no credentials provided
