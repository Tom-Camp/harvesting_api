from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PlantCreate(BaseModel):
    plant_type: str
    variety: str | None = None
    notes: str | None = None


class PlantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    garden_id: int
    plant_type: str
    variety: str | None = None
    added_at: datetime
    notes: str | None = None


class PlantUpdate(BaseModel):
    variety: str | None = None
    notes: str | None = None
