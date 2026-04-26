import uuid
from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from app.ai.garden_advisor import PlantCareOutput
from app.models.garden import Garden
from app.models.plant import Plant
from app.models.user import User


async def test_list_plants_empty(client: AsyncClient, test_garden: Garden):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_plants(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["species"] == test_plant.species
    assert data[0]["variety"] == test_plant.variety


async def test_add_plant(client: AsyncClient, test_garden: Garden):
    with patch("app.api.v1.plants._populate_latin_name", new=AsyncMock(return_value=None)):
        response = await client.post(
            f"/api/v1/gardens/{test_garden.slug}/plants",
            json={"plant_type": "vegetable", "species": "pepper", "variety": "bell"},
        )
    assert response.status_code == 201
    data = response.json()
    assert data["plant_type"] == "vegetable"
    assert data["species"] == "pepper"
    assert data["variety"] == "bell"
    assert data["notes"] == []


async def test_get_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["species"] == test_plant.species
    assert data["id"] == str(test_plant.id)


async def test_get_plant_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_update_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}",
        json={"variety": "roma"},
    )
    assert response.status_code == 200
    assert response.json()["variety"] == "roma"


async def test_delete_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.delete(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 404


async def test_plants_garden_not_found(client: AsyncClient):
    response = await client.get("/api/v1/gardens/no-such-garden/plants")
    assert response.status_code == 404


async def test_plants_require_active_account(pending_client: AsyncClient, test_garden: Garden):
    response = await pending_client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 403


async def test_archive_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")
    assert response.status_code == 200
    data = response.json()
    assert data["archived_at"] is not None


async def test_archive_plant_hidden_from_active_list(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 200
    assert response.json() == []


async def test_archived_plants_visible_with_filter(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants?archived=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_plant.id)


async def test_unarchive_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")

    response = await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/unarchive")
    assert response.status_code == 200
    assert response.json()["archived_at"] is None

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_archive_plant_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{uuid.uuid4()}/archive")
    assert response.status_code == 404


async def test_unarchive_plant_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{uuid.uuid4()}/unarchive")
    assert response.status_code == 404


async def test_archive_already_archived_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")
    response = await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")
    assert response.status_code == 200
    assert response.json()["archived_at"] is not None


async def test_unarchive_plant_not_archived(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/unarchive")
    assert response.status_code == 200
    assert response.json()["archived_at"] is None


async def test_archived_plant_retrievable_by_id(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 200
    assert response.json()["archived_at"] is not None


async def test_active_and_archived_plants_separated(
    client: AsyncClient, test_garden: Garden, test_plant: Plant, session
):
    active_plant = Plant(garden_id=test_garden.id, plant_type="herb", species="basil")
    session.add(active_plant)
    await session.commit()

    await client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")

    active_response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert active_response.status_code == 200
    active_ids = [p["id"] for p in active_response.json()]
    assert str(active_plant.id) in active_ids
    assert str(test_plant.id) not in active_ids

    archived_response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants?archived=true")
    assert archived_response.status_code == 200
    archived_ids = [p["id"] for p in archived_response.json()]
    assert str(test_plant.id) in archived_ids
    assert str(active_plant.id) not in archived_ids


async def test_non_member_cannot_archive_plant(
    session, second_user: User, test_garden: Garden, test_plant: Plant, second_client: AsyncClient
):
    response = await second_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive"
    )
    assert response.status_code in (403, 404)


async def test_member_can_add_plant(
    session, second_user: User, test_garden: Garden, second_client: AsyncClient
):
    from app.models.garden_member import GardenMember, GardenMemberRole
    session.add(GardenMember(garden_id=test_garden.id, user_id=second_user.id, role=GardenMemberRole.MEMBER))
    await session.commit()

    with patch("app.api.v1.plants._populate_latin_name", new=AsyncMock(return_value=None)):
        response = await second_client.post(
            f"/api/v1/gardens/{test_garden.slug}/plants",
            json={"plant_type": "herb", "species": "basil"},
        )
    assert response.status_code == 201
    assert response.json()["species"] == "basil"


async def test_member_can_update_plant(member_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await member_client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}",
        json={"variety": "updated-by-member"},
    )
    assert response.status_code == 200
    assert response.json()["variety"] == "updated-by-member"


async def test_member_can_archive_plant(member_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await member_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive"
    )
    assert response.status_code == 200
    assert response.json()["archived_at"] is not None


async def test_member_can_unarchive_plant(member_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await member_client.post(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/archive")
    response = await member_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/unarchive"
    )
    assert response.status_code == 200
    assert response.json()["archived_at"] is None


async def test_member_cannot_delete_plant(member_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await member_client.delete(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}"
    )
    assert response.status_code == 403


async def test_non_member_cannot_list_plants(second_client: AsyncClient, test_garden: Garden):
    response = await second_client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 403


async def test_non_member_cannot_get_plant(second_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await second_client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 403


async def test_non_member_cannot_update_plant(
    second_client: AsyncClient, test_garden: Garden, test_plant: Plant
):
    response = await second_client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}",
        json={"variety": "hijacked"},
    )
    assert response.status_code == 403


async def test_non_member_cannot_delete_plant(
    second_client: AsyncClient, test_garden: Garden, test_plant: Plant
):
    response = await second_client.delete(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}"
    )
    assert response.status_code == 403


async def test_unauthenticated_cannot_list_plants(unauthed_client: AsyncClient, test_garden: Garden):
    response = await unauthed_client.get(f"/api/v1/gardens/{test_garden.slug}/plants")
    assert response.status_code == 401


async def test_unauthenticated_cannot_create_plant(unauthed_client: AsyncClient, test_garden: Garden):
    response = await unauthed_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants",
        json={"plant_type": "herb", "species": "mint"},
    )
    assert response.status_code == 401


_MOCK_CARE = PlantCareOutput(
    planting="Plant 1cm deep",
    care="Water weekly",
    harvesting="Pick when ripe",
    summary="Easy to grow",
    latin_name="Solanum lycopersicum",
)


async def test_get_care_info(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    with patch("app.api.v1.plants.get_plant_tips", new=AsyncMock(return_value=_MOCK_CARE)):
        response = await client.post(
            f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/care"
        )
    assert response.status_code == 200
    data = response.json()
    assert data["latin_name"] == "Solanum lycopersicum"
    assert data["summary"] == "Easy to grow"


async def test_member_can_get_care_info(member_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    with patch("app.api.v1.plants.get_plant_tips", new=AsyncMock(return_value=_MOCK_CARE)):
        response = await member_client.post(
            f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/care"
        )
    assert response.status_code == 200


async def test_non_member_cannot_get_care_info(
    second_client: AsyncClient, test_garden: Garden, test_plant: Plant
):
    response = await second_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/care"
    )
    assert response.status_code == 403
