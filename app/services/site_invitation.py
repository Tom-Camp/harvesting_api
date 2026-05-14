from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.site_invitation import SiteInvitation


async def create_site_invitation(
    session: AsyncSession,
    email: str,
    invited_by_user_id: UUID,
) -> SiteInvitation:
    invitation = SiteInvitation(
        invited_email=email,
        invited_by_user_id=invited_by_user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)
    return invitation


async def get_site_invitation_by_token(session: AsyncSession, token: str) -> SiteInvitation | None:
    result = await session.execute(
        select(SiteInvitation).where(SiteInvitation.token == token)
    )
    return result.scalar_one_or_none()


async def list_site_invitations(session: AsyncSession) -> list[SiteInvitation]:
    result = await session.execute(select(SiteInvitation).order_by(SiteInvitation.created_at.desc()))  # type: ignore[arg-type]
    return list(result.scalars().all())


async def consume_site_invitation(session: AsyncSession, invitation: SiteInvitation) -> None:
    invitation.accepted_at = datetime.now(timezone.utc)
    session.add(invitation)
    await session.commit()


def validate_invitation(invitation: SiteInvitation, email: str) -> str | None:
    """Return an error message if the invitation is not usable, else None."""
    if invitation.accepted_at is not None:
        return "Invitation has already been used"
    now = datetime.now(timezone.utc)
    expires = invitation.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        return "Invitation has expired"
    if invitation.invited_email.lower() != email.lower():
        return "Invitation was issued for a different email address"
    return None
