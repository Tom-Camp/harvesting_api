import uuid
from typing import TYPE_CHECKING

from slugify import slugify
from sqlalchemy import event
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.plant import Plant
    from app.models.user import User


class Garden(ModelBase, table=True):

    user_id: uuid.UUID = Field(foreign_key="user.id", unique=True)
    name: str = Field(unique=True)
    slug: str = Field(unique=True, index=True)
    notes: str | None = None

    user: "User" = Relationship(back_populates="garden")
    plants: list["Plant"] = Relationship(back_populates="garden")


@event.listens_for(Garden, "before_insert")
@event.listens_for(Garden, "before_update")
def _set_slug(mapper, connection, target: Garden) -> None:
    target.slug = slugify(target.name)
