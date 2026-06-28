import uuid

from httpx import AsyncClient

from app.models.garden import Garden
from app.models.plant import Plant
from app.models.user import User


async def test_add_harvest(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 5, "unit": "kg"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 5
    assert data["unit"] == "kg"


async def test_add_harvest_sets_plant_unit(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 3, "unit": "lb"},
    )
    plant_response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert plant_response.json()["harvest_unit"] == "lb"


async def test_add_harvest_unit_mismatch(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 3, "unit": "kg"},
    )
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 2, "unit": "lb"},
    )
    assert response.status_code == 422
    assert "kg" in response.json()["detail"]


async def test_add_harvest_plant_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{uuid.uuid4()}/harvests",
        json={"amount": 1, "unit": "items"},
    )
    assert response.status_code == 404


async def test_update_harvest(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 3, "unit": "kg"},
    )
    harvest_id = create.json()["id"]

    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{harvest_id}",
        json={"amount": 10, "unit": "kg", "created_at": "2026-04-01T00:00:00Z"},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 10


async def test_update_harvest_partial(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 3, "unit": "kg"},
    )
    harvest_id = create.json()["id"]

    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{harvest_id}",
        json={"amount": 6},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 6
    assert response.json()["unit"] == "kg"


async def test_update_harvest_unit_mismatch(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 3, "unit": "kg"},
    )
    harvest_id = create.json()["id"]

    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{harvest_id}",
        json={"amount": 3, "unit": "lb", "created_at": "2026-04-01T00:00:00Z"},
    )
    assert response.status_code == 422


async def test_update_harvest_not_found(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{uuid.uuid4()}",
        json={"amount": 1, "unit": "items", "created_at": "2026-04-01T00:00:00Z"},
    )
    assert response.status_code == 404


async def test_delete_harvest(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 2, "unit": "items"},
    )
    harvest_id = create.json()["id"]

    response = await client.delete(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{harvest_id}"
    )
    assert response.status_code == 204


async def test_delete_harvest_not_found(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.delete(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{uuid.uuid4()}"
    )
    assert response.status_code == 404


async def test_harvest_appears_on_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 7, "unit": "items"},
    )
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 200
    harvests = response.json()["harvests"]
    assert any(h["amount"] == 7 for h in harvests)


async def test_member_can_add_harvest(member_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await member_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 3, "unit": "kg"},
    )
    assert response.status_code == 201
    assert response.json()["amount"] == 3


async def test_member_can_update_harvest(member_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await member_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 2, "unit": "kg"},
    )
    harvest_id = create.json()["id"]

    response = await member_client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{harvest_id}",
        json={"amount": 5, "unit": "kg", "created_at": "2026-04-01T00:00:00Z"},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 5


async def test_member_can_delete_harvest(member_client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await member_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 1, "unit": "items"},
    )
    harvest_id = create.json()["id"]

    response = await member_client.delete(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{harvest_id}"
    )
    assert response.status_code == 204


async def test_non_member_cannot_add_harvest(
    second_client: AsyncClient, test_garden: Garden, test_plant: Plant
):
    response = await second_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 1, "unit": "kg"},
    )
    assert response.status_code == 403


async def test_unauthenticated_cannot_add_harvest(
    unauthed_client: AsyncClient, test_garden: Garden, test_plant: Plant
):
    response = await unauthed_client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"amount": 1, "unit": "kg"},
    )
    assert response.status_code == 401
