import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if False:  # TYPE_CHECKING
    from app.models.user import User

TOKEN_TTL_MINUTES = 60


def _default_token() -> str:
    return secrets.token_urlsafe(32)


def _default_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES)


class PasswordResetToken(ModelBase, table=True):

    token: str = Field(default_factory=_default_token, unique=True, index=True)
    expires_at: datetime = Field(
        default_factory=_default_expires_at,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    used_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), nullable=True))
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship()
