import asyncio
from urllib.parse import urlencode

import httpx
import jwt
import structlog
from jwt import PyJWKClient

from app.utils.config import settings

logger = structlog.get_logger()

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"

_jwks_client = PyJWKClient(_GOOGLE_JWKS_URL, cache_keys=True)


def _redirect_uri() -> str:
    return f"{settings.app_base_url}/api/v1/auth/google/callback"


def build_authorization_url(state: str, nonce: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": _redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "nonce": nonce,
        "access_type": "online",
    }
    return f"{_GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_code_for_claims(code: str, nonce: str) -> dict[str, str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            _GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": _redirect_uri(),
                "grant_type": "authorization_code",
            },
        )
        if response.is_error:
            logger.error(
                "google_token_exchange_error",
                status_code=response.status_code,
                body=response.text,
            )
            response.raise_for_status()
        tokens = response.json()

    loop = asyncio.get_event_loop()
    signing_key = await loop.run_in_executor(
        None, _jwks_client.get_signing_key_from_jwt, tokens["id_token"]
    )
    claims: dict[str, str] = jwt.decode(
        tokens["id_token"],
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.google_client_id,
    )
    if claims.get("nonce") != nonce:
        raise ValueError("Nonce mismatch")
    return claims


async def prefetch_jwks() -> None:
    """Warm the JWKS cache on startup to avoid a blocking fetch on the first login."""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _jwks_client.fetch_data)
