from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_active_user
from app.db import get_session
from app.models.user import User
from app.schemas.garden_member import GardenMemberRead
from app.services import garden_member as member_service

router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("/{token}/accept", response_model=GardenMemberRead, status_code=status.HTTP_201_CREATED)
async def accept_invitation(
    token: str,
    user: User = Depends(require_active_user),
    session: AsyncSession = Depends(get_session),
) -> GardenMemberRead:
    invitation = await member_service.get_invitation_by_token(session, token)
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    try:
        member = await member_service.accept_invitation(session, invitation, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return GardenMemberRead.model_validate(member)
