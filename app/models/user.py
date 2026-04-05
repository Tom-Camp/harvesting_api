from __future__ import annotations

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.garden import Garden


class User(ModelBase, table=True):

    google_sub: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None
    location: str | None = None

    garden: Garden | None = Relationship(back_populates="user")
