import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.garden_member import GardenMemberRole
from app.schemas.user import UserRead


class GardenMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    garden_id: uuid.UUID
    user_id: uuid.UUID
    role: GardenMemberRole
    created_at: datetime
    user: UserRead


class GardenInvitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    garden_id: uuid.UUID
    invited_email: str
    token: str
    expires_at: datetime


class GardenMemberInvite(BaseModel):
    email: str
