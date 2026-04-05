import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.plant import CareInfo, PlantType


class NoteCreate(BaseModel):
    note: str


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    note: str | None
    created_at: datetime
    updated_at: datetime


class CareInfoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    planting: str | None
    care: str | None
    harvesting: str | None
    latin_name: str | None
    summary: str | None
    created_at: datetime
    updated_at: datetime


class PlantCreate(BaseModel):
    plant_type: PlantType
    species: str
    variety: str | None = None
    planted_date: datetime | None = None


class PlantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    garden_id: uuid.UUID
    plant_type: PlantType
    species: str
    variety: str | None = None
    notes: list[NoteRead] | None = None
    care_info: CareInfoRead | None
    created_at: datetime
    updated_at: datetime


class PlantUpdate(BaseModel):
    variety: str | None = None
    notes: str | None = None
    care: CareInfo | None = None
