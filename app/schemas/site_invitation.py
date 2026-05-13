import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class SiteInvitationCreate(BaseModel):
    email: EmailStr


class SiteInvitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    invited_email: str
    invited_by_user_id: uuid.UUID
    expires_at: datetime
    accepted_at: datetime | None = None
