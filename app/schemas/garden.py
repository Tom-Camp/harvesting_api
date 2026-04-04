from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GardenCreate(BaseModel):
    name: str


class GardenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    created_at: datetime


class GardenUpdate(BaseModel):
    name: str
