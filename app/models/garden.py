import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.garden_member import GardenInvitation, GardenMember
    from app.models.plant import Plant
    from app.models.user import User


class Garden(ModelBase, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    name: str
    slug: str = Field(default="", unique=True, index=True)
    location: str
    description: str | None = None

    user: "User" = Relationship(back_populates="gardens")
    plants: list["Plant"] = Relationship(back_populates="garden", cascade_delete=True)
    members: list["GardenMember"] = Relationship(back_populates="garden", cascade_delete=True)
    invitations: list["GardenInvitation"] = Relationship(back_populates="garden", cascade_delete=True)
