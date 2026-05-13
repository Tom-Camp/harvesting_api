from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site_invitation import SiteInvitation
from app.models.user import User, UserStatus


async def test_admin_can_invite_user(admin_client: AsyncClient):
    with patch("app.api.v1.admin.send_site_invitation_email", new=AsyncMock()) as mock_send:
        response = await admin_client.post(
            "/api/v1/admin/invitations",
            json={"email": "newuser@example.com"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["invited_email"] == "newuser@example.com"
    assert "token" not in data
    mock_send.assert_awaited_once()
    to_email, invite_url, inviter_name = mock_send.call_args.args
    assert to_email == "newuser@example.com"
    assert "register" in invite_url


async def test_non_admin_cannot_invite_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/admin/invitations",
        json={"email": "newuser@example.com"},
    )
    assert response.status_code == 403


async def test_admin_can_list_invitations(admin_client: AsyncClient, session: AsyncSession, admin_user: User):
    session.add(SiteInvitation(
        invited_email="someone@example.com",
        invited_by_user_id=admin_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    ))
    await session.commit()

    response = await admin_client.get("/api/v1/admin/invitations")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["invited_email"] == "someone@example.com"


async def test_non_admin_cannot_list_invitations(client: AsyncClient):
    response = await client.get("/api/v1/admin/invitations")
    assert response.status_code == 403


async def test_register_with_valid_invitation(
    unauthed_client: AsyncClient, session: AsyncSession, admin_user: User
):
    invitation = SiteInvitation(
        invited_email="invited@example.com",
        invited_by_user_id=admin_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)

    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={
            "email": "invited@example.com",
            "password": "Correct-Horse-Battery-Staple1!",
            "username": "inviteduser",
            "invitation_token": invitation.token,
        },
    )
    assert response.status_code == 201
    assert "pending" not in response.json()["message"].lower()

    await session.refresh(invitation)
    assert invitation.accepted_at is not None


async def test_register_with_valid_invitation_sets_active_status(
    unauthed_client: AsyncClient, session: AsyncSession, admin_user: User
):
    from sqlmodel import select
    from app.models.user import User as UserModel

    invitation = SiteInvitation(
        invited_email="active@example.com",
        invited_by_user_id=admin_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)

    await unauthed_client.post(
        "/api/v1/auth/register",
        json={
            "email": "active@example.com",
            "password": "Correct-Horse-Battery-Staple1!",
            "username": "activeuser",
            "invitation_token": invitation.token,
        },
    )

    result = await session.execute(select(UserModel).where(UserModel.email == "active@example.com"))
    user = result.scalar_one()
    assert user.status == UserStatus.ACTIVE


async def test_register_without_invitation_stays_pending(
    unauthed_client: AsyncClient, session: AsyncSession
):
    from sqlmodel import select
    from app.models.user import User as UserModel

    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={
            "email": "pending2@example.com",
            "password": "Correct-Horse-Battery-Staple1!",
            "username": "pendinguser2",
        },
    )
    assert response.status_code == 201
    assert "pending" in response.json()["message"].lower()

    result = await session.execute(select(UserModel).where(UserModel.email == "pending2@example.com"))
    user = result.scalar_one()
    assert user.status == UserStatus.PENDING


async def test_register_with_invalid_token(unauthed_client: AsyncClient):
    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "Correct-Horse-Battery-Staple1!",
            "username": "someuser",
            "invitation_token": "nonexistent-token",
        },
    )
    assert response.status_code == 400


async def test_register_with_expired_invitation(
    unauthed_client: AsyncClient, session: AsyncSession, admin_user: User
):
    invitation = SiteInvitation(
        invited_email="expired@example.com",
        invited_by_user_id=admin_user.id,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)

    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={
            "email": "expired@example.com",
            "password": "Correct-Horse-Battery-Staple1!",
            "username": "expireduser",
            "invitation_token": invitation.token,
        },
    )
    assert response.status_code == 400


async def test_register_with_already_used_invitation(
    unauthed_client: AsyncClient, session: AsyncSession, admin_user: User
):
    invitation = SiteInvitation(
        invited_email="used@example.com",
        invited_by_user_id=admin_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        accepted_at=datetime.now(timezone.utc),
    )
    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)

    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={
            "email": "used@example.com",
            "password": "Correct-Horse-Battery-Staple1!",
            "username": "useduser",
            "invitation_token": invitation.token,
        },
    )
    assert response.status_code == 400


async def test_register_with_wrong_email_invitation(
    unauthed_client: AsyncClient, session: AsyncSession, admin_user: User
):
    invitation = SiteInvitation(
        invited_email="correct@example.com",
        invited_by_user_id=admin_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)

    response = await unauthed_client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrong@example.com",
            "password": "Correct-Horse-Battery-Staple1!",
            "username": "wronguser",
            "invitation_token": invitation.token,
        },
    )
    assert response.status_code == 400
