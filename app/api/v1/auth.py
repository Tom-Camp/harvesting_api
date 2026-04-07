from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.tokens import create_access_token
from app.db import get_session
from app.models.user import UserStatus
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse
from app.services import garden_member as member_service
from app.services import user as user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    try:
        await user_service.create_user(
            session,
            email=str(data.email),
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return {"message": "Registration successful. Your account is pending admin approval."}


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    user = await user_service.authenticate(session, str(data.email), data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account pending approval")
    await member_service.accept_pending_invitations(session, user)
    return TokenResponse(access_token=create_access_token(user.id))
