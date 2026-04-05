import uuid

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship

from app.models.base import ModelBase

if TYPE_CHECKING:
    from app.models.garden import Garden


class PlantType(str, Enum):
    HERB = "herb"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    FLOWER = "flower"
    SHRUB = "shrub"
    TREE = "tree"
    VINE = "vine"


class Note(ModelBase, table=True):

    note: str | None
    plant_id: uuid.UUID = Field(foreign_key="plant.id")
    plant: "Plant" = Relationship(back_populates="notes")


class CareInfo(ModelBase, table=True):

    planting: str | None
    care: str | None
    harvesting: str | None
    summary: str | None
    latin_name: str | None
    plant_id: uuid.UUID = Field(foreign_key="plant.id")
    plant: "Plant" = Relationship(back_populates="care_info")


class Plant(ModelBase, table=True):

    plant_type: PlantType = Field(
        sa_column=Column(SAEnum(PlantType, values_callable=lambda x: [e.value for e in x]))
    )
    species: str
    variety: str | None = None
    planted_date: datetime | None = None
    notes: list[Note] = Relationship(back_populates="plant", cascade_delete=True)
    care_info: CareInfo | None = Relationship(back_populates="plant", cascade_delete=True)
    garden_id: uuid.UUID = Field(foreign_key="garden.id")
    garden: "Garden" = Relationship(back_populates="plants")
