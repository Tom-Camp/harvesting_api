import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GardenCreate(BaseModel):
    name: str
    location: str
    notes: str | None = None


class GardenUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    notes: str | None = None


class GardenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    slug: str
    location: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
