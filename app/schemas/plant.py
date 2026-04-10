import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.plant import CareInfo, Harvest, NoteLabel, PlantType


class NoteCreate(BaseModel):
    note: str
    label: NoteLabel = NoteLabel.NOTE


class NoteUpdate(BaseModel):
    note: str | None = None
    label: NoteLabel | None = None


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    note: str | None
    label: NoteLabel
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
    plot: str | None = None
    planted_date: datetime | None = None


class PlantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    garden_id: uuid.UUID
    plant_type: PlantType
    species: str
    variety: str | None = None
    notes: list[NoteRead] | None = None
    harvest: list[HarvestRead] | None = None
    care_info: CareInfoRead | None
    plot: str | None = None
    planted_date: datetime | None
    created_at: datetime
    updated_at: datetime


class PlantUpdate(BaseModel):
    variety: str | None = None
    notes: str | None = None
    plot: str | None = None
    planted_date: datetime | None = None
    care: CareInfo | None = None


class HarvestCreate(BaseModel):
    weight: float | None = None
    quantity: int | None = None


class HarvestUpdate(BaseModel):
    weight: float | None = None
    quantity: int | None = None


class HarvestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    weight: float | None = None
    quantity: int | None = None
    created_at: datetime
    updated_at: datetime
