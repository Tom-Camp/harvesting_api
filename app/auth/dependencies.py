import uuid
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.tokens import decode_access_token
from app.db import get_session
from app.models.garden import Garden
from app.models.garden_member import GardenMember, GardenMemberRole
from app.models.user import User, UserRole, UserStatus
from app.services import user as user_service

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_service.get_user(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_active_user(user: User = Depends(get_current_user)) -> User:
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account pending approval")
    return user


async def require_admin(user: User = Depends(require_active_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


@dataclass
class GardenAccess:
    garden: Garden
    member: GardenMember
    user: User

    @property
    def is_owner(self) -> bool:
        return self.member.role == GardenMemberRole.OWNER


async def require_garden_member(
    slug: str,
    user: User = Depends(require_active_user),
    session: AsyncSession = Depends(get_session),
) -> GardenAccess:
    from app.services import garden as garden_service
    from app.services import garden_member as member_service

    garden = await garden_service.get_garden_by_slug(session, slug)
    if not garden:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Garden not found")
    if user.role == UserRole.ADMIN:
        return GardenAccess(
            garden=garden,
            member=GardenMember(garden_id=garden.id, user_id=user.id, role=GardenMemberRole.OWNER),
            user=user,
        )
    member = await member_service.get_membership(session, garden.id, user.id)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this garden")
    return GardenAccess(garden=garden, member=member, user=user)


async def require_garden_owner(
    access: GardenAccess = Depends(require_garden_member),
) -> GardenAccess:
    if not access.is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required")
    return access
