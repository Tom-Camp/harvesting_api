import secrets
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.garden import Garden
    from app.models.user import User


class GardenMemberRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"


class GardenMember(ModelBase, table=True):
    __table_args__ = (UniqueConstraint("garden_id", "user_id"),)

    garden_id: uuid.UUID = Field(foreign_key="garden.id")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    role: GardenMemberRole = Field(
        default=GardenMemberRole.MEMBER,
        sa_column=Column(
            SAEnum(GardenMemberRole, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
        ),
    )

    garden: "Garden" = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="memberships")


class GardenInvitation(ModelBase, table=True):
    garden_id: uuid.UUID = Field(foreign_key="garden.id")
    invited_email: str = Field(index=True)
    invited_by_user_id: uuid.UUID = Field(foreign_key="user.id")
    token: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        unique=True,
        index=True,
    )
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    accepted_at: datetime | None = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))

    garden: "Garden" = Relationship(back_populates="invitations")
