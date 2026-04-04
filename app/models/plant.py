from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Plant(SQLModel, table=True):
    __tablename__ = "plants"

    id: int | None = Field(default=None, primary_key=True)
    garden_id: int = Field(foreign_key="gardens.id")
    plant_type: str
    variety: str | None = None
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str | None = None
