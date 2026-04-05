import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlantCreate(BaseModel):
    plant_type: str
    variety: str | None = None
    notes: str | None = None


class PlantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    garden_id: uuid.UUID
    plant_type: str
    variety: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class PlantUpdate(BaseModel):
    variety: str | None = None
    notes: str | None = None
