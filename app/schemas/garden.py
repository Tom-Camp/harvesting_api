import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.plant import NoteLabel


class GardenCreate(BaseModel):
    name: str
    location: str
    description: str | None = None


class GardenUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    description: str | None = None


class GardenNoteCreate(BaseModel):
    note: str
    label: NoteLabel = NoteLabel.NOTE


class GardenNoteUpdate(BaseModel):
    note: str | None = None
    label: NoteLabel | None = None


class GardenNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    note: str
    label: NoteLabel
    created_at: datetime
    updated_at: datetime


class GardenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    slug: str
    location: str
    description: str | None = None
    notes: list[GardenNoteRead] | None = None
    created_at: datetime
    updated_at: datetime
