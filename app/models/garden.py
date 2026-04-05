import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.plant import Plant
    from app.models.user import User


class Garden(ModelBase, table=True):

    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True)
    name: str
    notes: str | None = None

    user: "User" = Relationship(back_populates="garden")
    plants: list["Plant"] = Relationship(back_populates="garden")
