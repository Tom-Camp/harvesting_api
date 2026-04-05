from typing import TYPE_CHECKING, Optional

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

    garden: Optional["Garden"] = Relationship(back_populates="user")
