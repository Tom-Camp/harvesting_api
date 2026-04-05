from uuid import uuid4, UUID
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ModelBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column_kwargs={"server_default": func.now(), "onupdate": _utcnow},
    )
