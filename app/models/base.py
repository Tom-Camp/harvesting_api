from uuid import uuid4, UUID
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class ModelBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()}
    )
