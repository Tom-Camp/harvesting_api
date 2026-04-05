from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

from httpx import AsyncClient


async def test_google_login_returns_url_and_cookie(unauthed_client: AsyncClient):
    response = await unauthed_client.get("/api/v1/auth/google/login")
    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    parsed = urlparse(data["authorization_url"])
    params = parse_qs(parsed.query)
    assert "state" in params
    assert "nonce" in params
    assert "oauth_state" in response.cookies


async def test_google_callback_missing_cookie(unauthed_client: AsyncClient):
    response = await unauthed_client.get("/api/v1/auth/google/callback?code=abc&state=xyz")
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing state cookie"


async def test_google_callback_state_mismatch(unauthed_client: AsyncClient):
    await unauthed_client.get("/api/v1/auth/google/login")
    # Cookie is now set but we send the wrong state query param
    response = await unauthed_client.get(
        "/api/v1/auth/google/callback?code=abc&state=wrong-state-value"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "State mismatch"


async def test_google_callback_google_failure(unauthed_client: AsyncClient):
    login_response = await unauthed_client.get("/api/v1/auth/google/login")
    state = parse_qs(urlparse(login_response.json()["authorization_url"]).query)["state"][0]

    with patch("app.api.v1.auth.exchange_code_for_claims", side_effect=Exception("Google down")):
        response = await unauthed_client.get(
            f"/api/v1/auth/google/callback?code=fake_code&state={state}"
        )
    assert response.status_code == 502


async def test_google_callback_success(unauthed_client: AsyncClient):
    login_response = await unauthed_client.get("/api/v1/auth/google/login")
    state = parse_qs(urlparse(login_response.json()["authorization_url"]).query)["state"][0]

    fake_claims = {
        "sub": "google-sub-new-user",
        "email": "newuser@example.com",
        "given_name": "New",
        "family_name": "User",
    }
    with patch("app.api.v1.auth.exchange_code_for_claims", new=AsyncMock(return_value=fake_claims)):
        response = await unauthed_client.get(
            f"/api/v1/auth/google/callback?code=fake_code&state={state}"
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["profile_complete"] is False  # new user has no location
