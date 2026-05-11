from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate


async def test_register(unauthed_client: AsyncClient):
    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "username": "test_user",
            "password": "SecurePassword1!",
        },
    )
    assert response.status_code == 201
    assert "pending" in response.json()["message"].lower()


async def test_register_duplicate_email(unauthed_client: AsyncClient):
    payload = {
        "email": "dup@example.com",
        "username": "testuser2",
        "password": "SecurePassword1!",
    }
    await unauthed_client.post("/api/v1/auth/register", json=payload)
    response = await unauthed_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


async def test_register_password_too_weak(unauthed_client: AsyncClient):
    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "password123"},
    )
    assert response.status_code == 422


async def test_register_password_common_pattern(unauthed_client: AsyncClient):
    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={"email": "weak2@example.com", "password": "Short1!"},
    )
    assert response.status_code == 422


async def test_login_pending_user(unauthed_client: AsyncClient, session: AsyncSession):
    from app.services import user as user_service
    await user_service.create_user(
        session=session,
        user=UserCreate(
            email="pending@example.com", username="pending", password="incorrect hoarse tattery pin",
        )
    )

    response = await unauthed_client.post(
        "/api/v1/auth/login", json={"email": "pending@example.com", "password": "incorrect hoarse tattery pin"}
    )
    assert response.status_code == 403
    assert "pending" in response.json()["detail"].lower()


async def test_login_success(unauthed_client: AsyncClient, session: AsyncSession):
    from app.models.user import UserStatus
    from app.services import user as user_service

    user = await user_service.create_user(
        session=session,
        user=UserCreate(
            email="active@example.com", username="active", password="incorrect hoarse tattery pin",
        )
    )
    user.status = UserStatus.ACTIVE
    session.add(user)
    await session.commit()

    response = await unauthed_client.post(
        "/api/v1/auth/login", json={"email": "active@example.com", "password": "incorrect hoarse tattery pin"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(unauthed_client: AsyncClient, session: AsyncSession):
    from app.services import user as user_service
    await user_service.create_user(
        session=session,
        user=UserCreate(
            email="user@example.com", username="user", password="correct horse battery staple",
        ),
    )

    response = await unauthed_client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "incorrect hoarse tattery pin"}
    )
    assert response.status_code == 401
