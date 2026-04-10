import uuid

from httpx import AsyncClient

from app.models.garden import Garden
from app.models.plant import Plant


async def test_add_note(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes",
        json={"note": "First true leaves appeared"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["note"] == "First true leaves appeared"
    assert data["label"] == "note"


async def test_add_note_with_label(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes",
        json={"note": "Spotted aphids on leaves", "label": "pest"},
    )
    assert response.status_code == 201
    assert response.json()["label"] == "pest"


async def test_add_note_plant_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{uuid.uuid4()}/notes",
        json={"note": "Should fail"},
    )
    assert response.status_code == 404


async def test_update_note(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes",
        json={"note": "Original note"},
    )
    note_id = create.json()["id"]

    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes/{note_id}",
        json={"note": "Updated note", "label": "milestone"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["note"] == "Updated note"
    assert data["label"] == "milestone"


async def test_update_note_not_found(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes/{uuid.uuid4()}",
        json={"note": "Does not exist"},
    )
    assert response.status_code == 404


async def test_delete_note(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    create = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes",
        json={"note": "To be deleted"},
    )
    note_id = create.json()["id"]

    response = await client.delete(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes/{note_id}"
    )
    assert response.status_code == 204


async def test_delete_note_not_found(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    response = await client.delete(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes/{uuid.uuid4()}"
    )
    assert response.status_code == 404


async def test_note_appears_on_plant(client: AsyncClient, test_garden: Garden, test_plant: Plant):
    await client.post(
        f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}/notes",
        json={"note": "Visible on plant"},
    )
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/plants/{test_plant.id}")
    assert response.status_code == 200
    notes = response.json()["notes"]
    assert any(n["note"] == "Visible on plant" for n in notes)
