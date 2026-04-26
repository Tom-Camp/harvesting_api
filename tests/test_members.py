import uuid
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.garden import Garden
from app.models.garden_member import GardenMember, GardenMemberRole
from app.models.user import User


async def test_list_members(client: AsyncClient, test_garden: Garden):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/members")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["role"] == "owner"


async def test_list_members_not_a_member(second_client: AsyncClient, test_garden: Garden):
    response = await second_client.get(f"/api/v1/gardens/{test_garden.slug}/members")
    assert response.status_code == 403


async def test_invite_member(client: AsyncClient, test_garden: Garden):
    with patch("app.api.v1.members.send_invitation_email", new=AsyncMock()) as mock_send:
        response = await client.post(
            f"/api/v1/gardens/{test_garden.slug}/members/invite",
            json={"email": "newuser@example.com"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["invited_email"] == "newuser@example.com"
    assert "token" not in data
    mock_send.assert_awaited_once()
    to_email, invite_url, garden_name, inviter_name = mock_send.call_args.args
    assert to_email == "newuser@example.com"
    assert "accept-invitation" in invite_url


async def test_invite_member_non_owner_forbidden(
    session: AsyncSession, second_user: User, test_garden: Garden, second_client: AsyncClient
):
    session.add(GardenMember(garden_id=test_garden.id, user_id=second_user.id, role=GardenMemberRole.MEMBER))
    await session.commit()

    response = await second_client.post(
        f"/api/v1/gardens/{test_garden.slug}/members/invite",
        json={"email": "someone@example.com"},
    )
    assert response.status_code == 403


async def test_remove_member(
    session: AsyncSession, second_user: User, test_garden: Garden, client: AsyncClient
):
    session.add(GardenMember(garden_id=test_garden.id, user_id=second_user.id, role=GardenMemberRole.MEMBER))
    await session.commit()

    response = await client.delete(
        f"/api/v1/gardens/{test_garden.slug}/members/{second_user.id}"
    )
    assert response.status_code == 204


async def test_remove_member_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.delete(
        f"/api/v1/gardens/{test_garden.slug}/members/{uuid.uuid4()}"
    )
    assert response.status_code == 404


async def test_cannot_remove_owner(client: AsyncClient, test_garden: Garden, test_user: User):
    response = await client.delete(
        f"/api/v1/gardens/{test_garden.slug}/members/{test_user.id}"
    )
    assert response.status_code == 400


async def test_non_owner_cannot_remove_member(
    session: AsyncSession,
    second_user: User,
    test_garden: Garden,
    test_user: User,
    second_client: AsyncClient,
):
    session.add(GardenMember(garden_id=test_garden.id, user_id=second_user.id, role=GardenMemberRole.MEMBER))
    await session.commit()

    response = await second_client.delete(
        f"/api/v1/gardens/{test_garden.slug}/members/{test_user.id}"
    )
    assert response.status_code == 403


async def test_accept_invitation(
    session: AsyncSession,
    test_garden: Garden,
    test_user: User,
    second_user: User,
    second_client: AsyncClient,
):
    from app.services import garden_member as member_service

    invitation = await member_service.create_invitation(
        session,
        garden_id=test_garden.id,
        invited_by_user_id=test_user.id,
        email=second_user.email,
    )
    response = await second_client.post(f"/api/v1/invitations/{invitation.token}/accept")
    assert response.status_code == 201
    assert response.json()["role"] == "member"


async def test_accept_invitation_not_found(second_client: AsyncClient):
    response = await second_client.post("/api/v1/invitations/nonexistent-token/accept")
    assert response.status_code == 404


async def test_accept_invitation_already_accepted(
    session: AsyncSession,
    test_garden: Garden,
    test_user: User,
    second_user: User,
    second_client: AsyncClient,
):
    from app.services import garden_member as member_service

    invitation = await member_service.create_invitation(
        session,
        garden_id=test_garden.id,
        invited_by_user_id=test_user.id,
        email=second_user.email,
    )
    await second_client.post(f"/api/v1/invitations/{invitation.token}/accept")
    response = await second_client.post(f"/api/v1/invitations/{invitation.token}/accept")
    assert response.status_code == 400


async def test_member_can_list_members(member_client: AsyncClient, test_garden: Garden):
    response = await member_client.get(f"/api/v1/gardens/{test_garden.slug}/members")
    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_unauthenticated_cannot_list_members(unauthed_client: AsyncClient, test_garden: Garden):
    response = await unauthed_client.get(f"/api/v1/gardens/{test_garden.slug}/members")
    assert response.status_code == 401


async def test_unauthenticated_cannot_invite_member(unauthed_client: AsyncClient, test_garden: Garden):
    response = await unauthed_client.post(
        f"/api/v1/gardens/{test_garden.slug}/members/invite",
        json={"email": "someone@example.com"},
    )
    assert response.status_code == 401


async def test_unauthenticated_cannot_remove_member(
    unauthed_client: AsyncClient, test_garden: Garden, test_user: User
):
    response = await unauthed_client.delete(
        f"/api/v1/gardens/{test_garden.slug}/members/{test_user.id}"
    )
    assert response.status_code == 401
