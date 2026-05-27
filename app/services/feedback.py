import httpx

from app.schemas.feedback import FeedbackCreate
from app.utils.config import settings


async def create_github_issue(feedback: FeedbackCreate, submitted_by: str) -> str:
    body = feedback.description
    if submitted_by:
        body += f"\n\n---\n_Submitted by {submitted_by}_"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/repos/{settings.github_repo}/issues",
            headers={
                "Authorization": f"Bearer {settings.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={
                "title": feedback.title,
                "body": body,
                "labels": [feedback.type.value],
            },
        )
        response.raise_for_status()
        return str(response.json()["html_url"])
