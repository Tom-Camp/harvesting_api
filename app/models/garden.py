from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Garden(SQLModel, table=True):
    __tablename__ = "gardens"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
