import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import require_active_user
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services import feedback as feedback_service

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(require_active_user),
) -> FeedbackResponse:
    try:
        issue_url = await feedback_service.create_github_issue(payload, current_user.email)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to create GitHub issue",
        ) from exc
    return FeedbackResponse(issue_url=issue_url)
