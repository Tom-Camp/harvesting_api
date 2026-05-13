import logging

import httpx

from app.utils.config import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


async def send_invitation_email(to_email: str, invite_url: str, garden_name: str, inviter_name: str) -> None:
    payload = {
        "from": settings.resend_from_email,
        "to": [to_email],
        "subject": f"You've been invited to join {garden_name} on Harvesting.food",
        "html": (
            f"<p>{inviter_name} has invited you to join <strong>{garden_name}</strong> on Harvesting.Food.</p>"
            f'<p><a href="{invite_url}">Accept your invitation</a></p>'
            "<p>This link expires in 7 days. If you did not expect this invitation, you can ignore this email.</p>"
        ),
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            RESEND_API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            timeout=10,
        )
        response.raise_for_status()


async def send_site_invitation_email(to_email: str, invite_url: str, inviter_name: str) -> None:
    payload = {
        "from": settings.resend_from_email,
        "to": [to_email],
        "subject": "You've been invited to join Harvesting.food",
        "html": (
            f"<p>{inviter_name} has invited you to join <strong>Harvesting.Food</strong>.</p>"
            f'<p><a href="{invite_url}">Create your account</a></p>'
            "<p>This link expires in 7 days. If you did not expect this invitation, you can ignore this email.</p>"
        ),
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            RESEND_API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            timeout=10,
        )
        response.raise_for_status()


async def send_password_reset_email(to_email: str, reset_url: str) -> None:
    payload = {
        "from": settings.resend_from_email,
        "to": [to_email],
        "subject": "Reset your Harvesting.food password",
        "html": (
            "<p>You requested a password reset for your Harvesting.Food account.</p>"
            f'<p><a href="{reset_url}">Reset your password</a></p>'
            "<p>This link expires in 60 minutes. If you did not request this, you can ignore this email.</p>"
        ),
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            RESEND_API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            timeout=10,
        )
        response.raise_for_status()
