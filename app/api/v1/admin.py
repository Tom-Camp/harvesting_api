import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.dependencies import require_admin
from app.db import get_session
from app.email.resend import send_site_invitation_email
from app.models.user import User, UserStatus
from app.schemas.site_invitation import SiteInvitationCreate, SiteInvitationRead
from app.schemas.user import SetRoleRequest, UserRead
from app.services import garden_member as member_service
from app.services import site_invitation as site_invitation_service
from app.services import user as user_service
from app.utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRead])
async def list_users(
    filter_status: UserStatus | None = Query(default=None, alias="status"),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[UserRead]:
    query = select(User)
    if filter_status is not None:
        query = query.where(User.status == filter_status)
    result = await session.execute(query)
    return [UserRead.model_validate(u) for u in result.scalars().all()]


@router.patch("/users/{user_id}/approve", response_model=UserRead)
async def approve_user(
    user_id: uuid.UUID,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    user = await user_service.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = await user_service.approve_user(session, user)
    await member_service.accept_pending_invitations(session, user)
    return UserRead.model_validate(user)


@router.patch("/users/{user_id}/suspend", response_model=UserRead)
async def suspend_user(
    user_id: uuid.UUID,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    user = await user_service.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = await user_service.suspend_user(session, user)
    return UserRead.model_validate(user)


@router.post("/invitations", response_model=SiteInvitationRead, status_code=status.HTTP_201_CREATED)
async def invite_user(
    data: SiteInvitationCreate,
    admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> SiteInvitationRead:
    invitation = await site_invitation_service.create_site_invitation(
        session, email=str(data.email), invited_by_user_id=admin.id
    )
    invite_url = f"{settings.app_base_url}/register?token={invitation.token}"
    inviter_name = " ".join(filter(None, [admin.first_name, admin.last_name])) or admin.email
    try:
        await send_site_invitation_email(str(data.email), invite_url, inviter_name)
    except Exception:
        logger.exception("Failed to send site invitation email to %s", data.email)
    return SiteInvitationRead.model_validate(invitation)


@router.get("/invitations", response_model=list[SiteInvitationRead])
async def list_invitations(
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[SiteInvitationRead]:
    invitations = await site_invitation_service.list_site_invitations(session)
    return [SiteInvitationRead.model_validate(i) for i in invitations]


@router.patch("/users/{user_id}/role", response_model=UserRead)
async def set_user_role(
    user_id: uuid.UUID,
    data: SetRoleRequest,
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    user = await user_service.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = await user_service.set_role(session, user, data.role)
    return UserRead.model_validate(user)
