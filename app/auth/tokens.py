import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.utils.config import settings


def create_access_token(user_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> uuid.UUID:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return uuid.UUID(payload["sub"])


def create_state_cookie(state: str, nonce: str) -> str:
    """Encode OAuth state + nonce into a short-lived signed JWT for the callback cookie."""
    payload = {
        "state": state,
        "nonce": nonce,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_state_cookie(cookie: str) -> tuple[str, str]:
    """Decode and verify the OAuth state cookie. Returns (state, nonce)."""
    payload = jwt.decode(cookie, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return payload["state"], payload["nonce"]
