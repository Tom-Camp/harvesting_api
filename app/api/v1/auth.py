import secrets

import jwt
import structlog
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.google import build_authorization_url, exchange_code_for_claims
from app.auth.tokens import create_access_token, create_state_cookie, decode_state_cookie
from app.db import get_session
from app.schemas.user import TokenResponse
from app.services import user as user_service

router = APIRouter(prefix="/auth", tags=["auth"])
logger = structlog.get_logger()

_STATE_COOKIE = "oauth_state"


@router.get("/google/login")
async def google_login(response: Response) -> dict[str, str]:
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    response.set_cookie(
        _STATE_COOKIE,
        create_state_cookie(state, nonce),
        httponly=True,
        max_age=600,
        samesite="lax",
        secure=False,  # TODO: set True when deployed over HTTPS
    )
    return {"authorization_url": build_authorization_url(state, nonce)}


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(
    code: str,
    state: str,
    response: Response,
    oauth_state: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    if not oauth_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing state cookie")

    try:
        cookie_state, nonce = decode_state_cookie(oauth_state)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state cookie")

    if cookie_state != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State mismatch")

    response.delete_cookie(_STATE_COOKIE)

    try:
        claims = await exchange_code_for_claims(code, nonce)
    except Exception:
        logger.exception("google_token_exchange_failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google authentication failed",
        )

    user = await user_service.find_or_create_from_google(session, claims)
    logger.info("user_authenticated", user_id=user.id, email=user.email)

    return TokenResponse(
        access_token=create_access_token(user.id),
        token_type="bearer",
        profile_complete=user.location is not None,
    )
