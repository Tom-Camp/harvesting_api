import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import GardenAccess, require_garden_member, require_garden_owner
from app.db import get_session
from app.models.garden_member import GardenMemberRole
from app.schemas.garden_member import GardenInvitationRead, GardenMemberInvite, GardenMemberRead
from app.services import garden_member as member_service

router = APIRouter(prefix="/gardens/{slug}/members", tags=["members"])


@router.get("", response_model=list[GardenMemberRead])
async def list_members(
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> list[GardenMemberRead]:
    members = await member_service.list_members(session, access.garden.id)
    return [GardenMemberRead.model_validate(m) for m in members]


@router.post("/invite", response_model=GardenInvitationRead, status_code=status.HTTP_201_CREATED)
async def invite_member(
    data: GardenMemberInvite,
    access: GardenAccess = Depends(require_garden_owner),
    session: AsyncSession = Depends(get_session),
) -> GardenInvitationRead:
    invitation = await member_service.create_invitation(
        session,
        garden_id=access.garden.id,
        invited_by_user_id=access.user.id,
        email=data.email,
    )
    return GardenInvitationRead.model_validate(invitation)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_owner),
    session: AsyncSession = Depends(get_session),
) -> None:
    member = await member_service.get_membership(session, access.garden.id, user_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == GardenMemberRole.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the garden owner")
    await member_service.remove_member(session, member)
