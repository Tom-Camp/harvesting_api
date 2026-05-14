import secrets
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field

from app.models.base import ModelBase

if TYPE_CHECKING:
    pass


class SiteInvitation(ModelBase, table=True):
    invited_email: str = Field(index=True)
    invited_by_user_id: uuid.UUID = Field(foreign_key="user.id")
    token: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        unique=True,
        index=True,
    )
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    accepted_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
