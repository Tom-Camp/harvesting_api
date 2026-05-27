from enum import StrEnum

from pydantic import BaseModel


class FeedbackType(StrEnum):
    bug = "bug"
    enhancement = "enhancement"


class FeedbackCreate(BaseModel):
    type: FeedbackType
    title: str
    description: str


class FeedbackResponse(BaseModel):
    issue_url: str
