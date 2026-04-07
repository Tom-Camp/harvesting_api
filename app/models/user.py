from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.garden import Garden
    from app.models.garden_member import GardenMember


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(ModelBase, table=True):
    email: str = Field(unique=True, index=True)
    password_hash: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None
    status: UserStatus = Field(
        default=UserStatus.PENDING,
        sa_column=Column(
            SAEnum(UserStatus, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
        ),
    )
    role: UserRole = Field(
        default=UserRole.USER,
        sa_column=Column(
            SAEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
        ),
    )

    gardens: list["Garden"] = Relationship(back_populates="user")
    memberships: list["GardenMember"] = Relationship(back_populates="user")
