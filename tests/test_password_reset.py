from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus
from app.schemas.user import UserCreate


async def _active_user(session: AsyncSession, email: str = "reset@example.com") -> User:
    from app.services import user as user_service
    user = await user_service.create_user(
        session=session,
        user=UserCreate(
            email=email, username="active", password="incorrect hoarse tattery pin",
        )
    )
    user.status = UserStatus.ACTIVE
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# POST /auth/forgot-password
# ---------------------------------------------------------------------------

async def test_forgot_password_sends_email(unauthed_client: AsyncClient, session: AsyncSession):
    await _active_user(session)

    with patch("app.api.v1.auth.send_password_reset_email", new=AsyncMock()) as mock_send:
        response = await unauthed_client.post(
            "/api/v1/auth/forgot-password", json={"email": "reset@example.com"}
        )

    assert response.status_code == 200
    mock_send.assert_awaited_once()
    _, reset_url = mock_send.call_args.args
    assert "token=" in reset_url


async def test_forgot_password_unknown_email_still_200(unauthed_client: AsyncClient):
    """Never leak whether an email is registered."""
    with patch("app.api.v1.auth.send_password_reset_email", new=AsyncMock()) as mock_send:
        response = await unauthed_client.post(
            "/api/v1/auth/forgot-password", json={"email": "nobody@example.com"}
        )

    assert response.status_code == 200
    mock_send.assert_not_awaited()


async def test_forgot_password_email_failure_still_200(unauthed_client: AsyncClient, session: AsyncSession):
    """A Resend API error must not surface to the caller."""
    await _active_user(session)

    with patch("app.api.v1.auth.send_password_reset_email", new=AsyncMock(side_effect=Exception("smtp down"))):
        response = await unauthed_client.post(
            "/api/v1/auth/forgot-password", json={"email": "reset@example.com"}
        )

    assert response.status_code == 200


# ---------------------------------------------------------------------------
# POST /auth/reset-password
# ---------------------------------------------------------------------------

async def test_reset_password_success(unauthed_client: AsyncClient, session: AsyncSession):
    user = await _active_user(session)

    from app.services import password_reset as reset_service
    token = await reset_service.create_reset_token(session, user)

    response = await unauthed_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token.token, "password": "NewPassword1!"},
    )
    assert response.status_code == 200

    # Login with the new password should now work
    login = await unauthed_client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "NewPassword1!"}
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


async def test_reset_password_old_password_rejected(unauthed_client: AsyncClient, session: AsyncSession):
    user = await _active_user(session)

    from app.services import password_reset as reset_service
    token = await reset_service.create_reset_token(session, user)

    await unauthed_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token.token, "password": "NewPassword1!"},
    )

    login = await unauthed_client.post(
        "/api/v1/auth/login", json={"email": user.email, "password": "OldPassword1!"}
    )
    assert login.status_code == 401


async def test_reset_password_invalid_token(unauthed_client: AsyncClient):
    response = await unauthed_client.post(
        "/api/v1/auth/reset-password",
        json={"token": "not-a-real-token", "password": "NewPassword1!"},
    )
    assert response.status_code == 400


async def test_reset_password_token_already_used(unauthed_client: AsyncClient, session: AsyncSession):
    user = await _active_user(session)

    from app.services import password_reset as reset_service
    token = await reset_service.create_reset_token(session, user)

    await unauthed_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token.token, "password": "NewPassword1!"},
    )
    response = await unauthed_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token.token, "password": "AnotherPassword1!"},
    )
    assert response.status_code == 400


async def test_reset_password_expired_token(unauthed_client: AsyncClient, session: AsyncSession):
    user = await _active_user(session)

    from app.models.password_reset import PasswordResetToken
    expired = PasswordResetToken(
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    session.add(expired)
    await session.commit()
    await session.refresh(expired)

    response = await unauthed_client.post(
        "/api/v1/auth/reset-password",
        json={"token": expired.token, "password": "NewPassword1!"},
    )
    assert response.status_code == 400


async def test_reset_password_weak_password(unauthed_client: AsyncClient, session: AsyncSession):
    user = await _active_user(session)

    from app.services import password_reset as reset_service
    token = await reset_service.create_reset_token(session, user)

    response = await unauthed_client.post(
        "/api/v1/auth/reset-password",
        json={"token": token.token, "password": "password123"},
    )
    assert response.status_code == 422
