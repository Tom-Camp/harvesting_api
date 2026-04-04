from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    google_sub: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    first_name: str | None = None
    last_name: str | None = None
    picture: str | None = None
    location: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
