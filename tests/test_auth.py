from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


async def test_register(unauthed_client: AsyncClient):
    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "SecurePassword1!"},
    )
    assert response.status_code == 201
    assert "pending" in response.json()["message"].lower()


async def test_register_duplicate_email(unauthed_client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "SecurePassword1!"}
    await unauthed_client.post("/api/v1/auth/register", json=payload)
    response = await unauthed_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


async def test_register_password_too_short(unauthed_client: AsyncClient):
    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "Short1!"},
    )
    assert response.status_code == 422


async def test_register_password_all_lowercase(unauthed_client: AsyncClient):
    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "alllowercasepassword"},
    )
    assert response.status_code == 422


async def test_login_pending_user(unauthed_client: AsyncClient, session: AsyncSession):
    from app.services import user as user_service
    await user_service.create_user(session, email="pending@example.com", password="pass")

    response = await unauthed_client.post(
        "/api/v1/auth/login", json={"email": "pending@example.com", "password": "pass"}
    )
    assert response.status_code == 403
    assert "pending" in response.json()["detail"].lower()


async def test_login_success(unauthed_client: AsyncClient, session: AsyncSession):
    from app.models.user import UserStatus
    from app.services import user as user_service

    user = await user_service.create_user(session, email="active@example.com", password="pass")
    user.status = UserStatus.ACTIVE
    session.add(user)
    await session.commit()

    response = await unauthed_client.post(
        "/api/v1/auth/login", json={"email": "active@example.com", "password": "pass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(unauthed_client: AsyncClient, session: AsyncSession):
    from app.services import user as user_service
    await user_service.create_user(session, email="user@example.com", password="correct")

    response = await unauthed_client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
