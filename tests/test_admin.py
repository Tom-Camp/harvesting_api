import uuid

from httpx import AsyncClient

from app.models.user import User


async def test_list_users(admin_client: AsyncClient, test_user: User):
    response = await admin_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()]
    assert test_user.email in emails


async def test_list_users_filter_by_status(admin_client: AsyncClient, pending_user: User, test_user: User):
    response = await admin_client.get("/api/v1/admin/users?status=pending")
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()]
    assert pending_user.email in emails
    assert test_user.email not in emails


async def test_list_users_non_admin_forbidden(client: AsyncClient):
    response = await client.get("/api/v1/admin/users")
    assert response.status_code == 403


async def test_approve_user(admin_client: AsyncClient, pending_user: User):
    response = await admin_client.patch(f"/api/v1/admin/users/{pending_user.id}/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "active"


async def test_approve_user_not_found(admin_client: AsyncClient):
    response = await admin_client.patch(f"/api/v1/admin/users/{uuid.uuid4()}/approve")
    assert response.status_code == 404


async def test_suspend_user(admin_client: AsyncClient, test_user: User):
    response = await admin_client.patch(f"/api/v1/admin/users/{test_user.id}/suspend")
    assert response.status_code == 200
    assert response.json()["status"] == "suspended"


async def test_suspend_user_not_found(admin_client: AsyncClient):
    response = await admin_client.patch(f"/api/v1/admin/users/{uuid.uuid4()}/suspend")
    assert response.status_code == 404


async def test_set_user_role(admin_client: AsyncClient, test_user: User):
    response = await admin_client.patch(
        f"/api/v1/admin/users/{test_user.id}/role",
        json={"role": "admin"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


async def test_set_user_role_not_found(admin_client: AsyncClient):
    response = await admin_client.patch(
        f"/api/v1/admin/users/{uuid.uuid4()}/role",
        json={"role": "admin"},
    )
    assert response.status_code == 404
