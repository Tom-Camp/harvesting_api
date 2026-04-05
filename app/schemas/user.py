import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None
    location: str | None = None
    created_at: datetime
    updated_at: datetime


class ProfileUpdate(BaseModel):
    location: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile_complete: bool
