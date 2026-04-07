from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.garden_member import GardenInvitation, GardenMember, GardenMemberRole
from app.models.user import User


async def get_membership(session: AsyncSession, garden_id: UUID, user_id: UUID) -> GardenMember | None:
    result = await session.execute(
        select(GardenMember).where(
            GardenMember.garden_id == garden_id,
            GardenMember.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def list_members(session: AsyncSession, garden_id: UUID) -> list[GardenMember]:
    result = await session.execute(
        select(GardenMember)
        .where(GardenMember.garden_id == garden_id)
        .options(selectinload(GardenMember.user))  # type: ignore[arg-type]
    )
    return list(result.scalars().all())


async def create_invitation(
    session: AsyncSession,
    garden_id: UUID,
    invited_by_user_id: UUID,
    email: str,
) -> GardenInvitation:
    invitation = GardenInvitation(
        garden_id=garden_id,
        invited_by_user_id=invited_by_user_id,
        invited_email=email,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)
    return invitation


async def get_invitation_by_token(session: AsyncSession, token: str) -> GardenInvitation | None:
    result = await session.execute(
        select(GardenInvitation).where(GardenInvitation.token == token)
    )
    return result.scalar_one_or_none()


async def accept_invitation(session: AsyncSession, invitation: GardenInvitation, user: User) -> GardenMember:
    now = datetime.now(timezone.utc)
    expires = invitation.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        raise ValueError("Invitation has expired")
    if invitation.accepted_at is not None:
        raise ValueError("Invitation already accepted")

    member = GardenMember(garden_id=invitation.garden_id, user_id=user.id, role=GardenMemberRole.MEMBER)
    session.add(member)
    invitation.accepted_at = now
    session.add(invitation)
    await session.commit()

    result = await session.execute(
        select(GardenMember)
        .where(GardenMember.id == member.id)
        .options(selectinload(GardenMember.user))  # type: ignore[arg-type]
    )
    return result.scalar_one()


async def remove_member(session: AsyncSession, member: GardenMember) -> None:
    await session.delete(member)
    await session.commit()


async def accept_pending_invitations(session: AsyncSession, user: User) -> None:
    """Auto-accept any pending invitations matching the user's email."""
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(GardenInvitation).where(
            GardenInvitation.invited_email == user.email,
            GardenInvitation.accepted_at.is_(None),  # type: ignore[union-attr]
            GardenInvitation.expires_at > now,
        )
    )
    invitations = list(result.scalars().all())
    for invitation in invitations:
        existing = await get_membership(session, invitation.garden_id, user.id)
        if not existing:
            session.add(GardenMember(
                garden_id=invitation.garden_id,
                user_id=user.id,
                role=GardenMemberRole.MEMBER,
            ))
        invitation.accepted_at = now
        session.add(invitation)
    if invitations:
        await session.commit()
