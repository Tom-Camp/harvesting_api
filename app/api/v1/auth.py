import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.tokens import create_access_token
from app.db import get_session
from app.email.resend import send_password_reset_email
from app.models.user import UserStatus
from app.schemas.user import ForgotPasswordRequest, UserLogin, UserCreate, ResetPasswordRequest, TokenResponse
from app.services import garden_member as member_service
from app.services import password_reset as reset_service
from app.services import user as user_service
from app.utils.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    try:
        await user_service.create_user(
            session=session,
            user=user,
        )
    except IntegrityError as exc:
        detail = "Username already taken" if "username" in str(exc.orig).lower() else "Email already registered"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return {"message": "Registration successful. Your account is pending admin approval."}


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    user = await user_service.authenticate(session=session, user_data=data)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account suspended")
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account pending approval")
    await member_service.accept_pending_invitations(session, user)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    data: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    user = await reset_service.get_user_by_email(session, str(data.email))
    if user:
        try:
            token = await reset_service.create_reset_token(session, user)
            reset_url = f"{settings.app_base_url}/reset-password?token={token.token}"
            await send_password_reset_email(user.email, reset_url)
        except Exception:
            logger.exception("Failed to send password reset email to %s", user.email)
    return {"message": "If that email is registered you will receive a reset link shortly."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    data: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    record = await reset_service.get_valid_token(session, data.token)
    if not record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    await reset_service.consume_token(session, record, data.password)
    return {"message": "Password reset successful."}
