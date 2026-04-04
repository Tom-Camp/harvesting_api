from enum import StrEnum

from pydantic import BaseModel


class TipMode(StrEnum):
    PLANTING = "planting"
    CARE = "care"
    HARVEST = "harvest"


class TipSection(BaseModel):
    title: str
    content: str


class GardenTipsResponse(BaseModel):
    mode: TipMode
    plant_type: str
    variety: str | None = None
    location: str | None = None
    tips: list[TipSection]
    summary: str
