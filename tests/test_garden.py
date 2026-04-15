import uuid

from httpx import AsyncClient

from app.models.garden import Garden
from app.models.user import User


async def test_create_garden(client: AsyncClient, test_user: User):
    response = await client.post("/api/v1/gardens", json={"name": "Veggie Patch", "location": "Portland, OR"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Veggie Patch"
    assert data["slug"] == "veggie-patch"
    assert data["location"] == "Portland, OR"
    assert data["user_id"] == str(test_user.id)


async def test_create_garden_slug_auto_suffix(client: AsyncClient, test_garden: Garden):
    """Second garden with the same name gets an auto-suffixed slug."""
    response = await client.post("/api/v1/gardens", json={"name": "My Test Garden", "location": "Denver, CO"})
    assert response.status_code == 201
    assert response.json()["slug"] == "my-test-garden-2"


async def test_list_gardens(client: AsyncClient, test_garden: Garden):
    response = await client.get("/api/v1/gardens")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["slug"] == test_garden.slug


async def test_list_gardens_empty(client: AsyncClient, test_user: User):
    response = await client.get("/api/v1/gardens")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_garden(client: AsyncClient, test_garden: Garden):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}")
    assert response.status_code == 200
    assert response.json()["name"] == test_garden.name


async def test_get_garden_not_found(client: AsyncClient):
    response = await client.get("/api/v1/gardens/does-not-exist")
    assert response.status_code == 404


async def test_update_garden(client: AsyncClient, test_garden: Garden):
    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}",
        json={"name": "Updated Name", "location": "Seattle, WA"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["location"] == "Seattle, WA"
    assert data["slug"] == test_garden.slug  # slug unchanged on rename


async def test_garden_requires_active_account(pending_client: AsyncClient):
    response = await pending_client.get("/api/v1/gardens/any-slug")
    assert response.status_code == 403


async def test_non_member_forbidden(second_client: AsyncClient, test_garden: Garden):
    response = await second_client.get(f"/api/v1/gardens/{test_garden.slug}")
    assert response.status_code == 403


async def test_non_owner_cannot_update(
    session, second_user: User, test_garden: Garden, second_client: AsyncClient
):
    from app.models.garden_member import GardenMember, GardenMemberRole
    session.add(GardenMember(garden_id=test_garden.id, user_id=second_user.id, role=GardenMemberRole.MEMBER))
    await session.commit()

    response = await second_client.patch(
        f"/api/v1/gardens/{test_garden.slug}", json={"name": "Hijacked"}
    )
    assert response.status_code == 403


async def test_delete_garden(client: AsyncClient, test_garden: Garden):
    response = await client.delete(f"/api/v1/gardens/{test_garden.slug}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}")
    assert response.status_code == 404


async def test_non_owner_cannot_delete_garden(
    session, second_user: User, test_garden: Garden, second_client: AsyncClient
):
    from app.models.garden_member import GardenMember, GardenMemberRole
    session.add(GardenMember(garden_id=test_garden.id, user_id=second_user.id, role=GardenMemberRole.MEMBER))
    await session.commit()

    response = await second_client.delete(f"/api/v1/gardens/{test_garden.slug}")
    assert response.status_code == 403


async def test_non_member_cannot_delete_garden(second_client: AsyncClient, test_garden: Garden):
    response = await second_client.delete(f"/api/v1/gardens/{test_garden.slug}")
    assert response.status_code == 403
