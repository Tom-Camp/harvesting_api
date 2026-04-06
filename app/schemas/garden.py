import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GardenCreate(BaseModel):
    name: str


class GardenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime


class GardenUpdate(BaseModel):
    name: str
