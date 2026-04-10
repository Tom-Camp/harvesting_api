import uuid

from httpx import AsyncClient

from app.models.garden import Garden
from app.models.plant import Plant


async def test_add_harvest(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"quantity": 5, "weight": 1.2},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 5
    assert data["weight"] == 1.2


async def test_add_harvest_weight_only(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"weight": 0.75},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["weight"] == 0.75
    assert data["quantity"] is None


async def test_add_harvest_plant_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{uuid.uuid4()}/harvests",
        json={"quantity": 1},
    )
    assert response.status_code == 404


async def test_update_harvest(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"quantity": 3},
    )
    harvest_id = create.json()["id"]

    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{harvest_id}",
        json={"quantity": 10, "weight": 2.5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 10
    assert data["weight"] == 2.5


async def test_update_harvest_not_found(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests/{uuid.uuid4()}",
        json={"quantity": 1},
    )
    assert response.status_code == 404


async def test_delete_harvest(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/harvests",
        json={"quantity": 2},
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
        json={"quantity": 7, "weight": 3.0},
    )
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 200
    harvests = response.json()["harvest"]
    assert any(h["quantity"] == 7 for h in harvests)
