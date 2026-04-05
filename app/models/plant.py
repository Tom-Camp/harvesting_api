from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.garden import Garden


class Plant(ModelBase, table=True):

    garden_id: uuid.UUID = Field(foreign_key="garden.id")
    plant_type: str
    variety: str | None = None
    notes: str | None = None

    garden: Garden = Relationship(back_populates="plants")
