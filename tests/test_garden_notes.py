import uuid

from httpx import AsyncClient

from app.models.garden import Garden


async def test_add_garden_note(client: AsyncClient, test_garden: Garden):
    response = await client.post(
        f"/api/v1/gardens/{test_garden.slug}/notes",
        json={"note": "Planted the spring beds"},
    )
    assert response.status_code == 201
    assert response.json()["note"] == "Planted the spring beds"


async def test_add_garden_note_garden_not_found(client: AsyncClient):
    response = await client.post(
        "/api/v1/gardens/does-not-exist/notes",
        json={"note": "Should fail"},
    )
    assert response.status_code == 404


async def test_list_garden_notes(client: AsyncClient, test_garden: Garden):
    await client.post(f"/api/v1/gardens/{test_garden.slug}/notes", json={"note": "First note"})
    await client.post(f"/api/v1/gardens/{test_garden.slug}/notes", json={"note": "Second note"})

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/notes")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 2
    assert {n["note"] for n in notes} == {"First note", "Second note"}


async def test_get_garden_note(client: AsyncClient, test_garden: Garden):
    create = await client.post(f"/api/v1/gardens/{test_garden.slug}/notes", json={"note": "Original note"})
    note_id = create.json()["id"]

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["note"] == "Original note"


async def test_get_garden_note_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/notes/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_update_garden_note(client: AsyncClient, test_garden: Garden):
    create = await client.post(f"/api/v1/gardens/{test_garden.slug}/notes", json={"note": "Original note"})
    note_id = create.json()["id"]

    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/notes/{note_id}",
        json={"note": "Updated note"},
    )
    assert response.status_code == 200
    assert response.json()["note"] == "Updated note"


async def test_update_garden_note_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.patch(
        f"/api/v1/gardens/{test_garden.slug}/notes/{uuid.uuid4()}",
        json={"note": "Does not exist"},
    )
    assert response.status_code == 404


async def test_delete_garden_note(client: AsyncClient, test_garden: Garden):
    create = await client.post(f"/api/v1/gardens/{test_garden.slug}/notes", json={"note": "To be deleted"})
    note_id = create.json()["id"]

    response = await client.delete(f"/api/v1/gardens/{test_garden.slug}/notes/{note_id}")
    assert response.status_code == 204

    response = await client.get(f"/api/v1/gardens/{test_garden.slug}/notes/{note_id}")
    assert response.status_code == 404


async def test_delete_garden_note_not_found(client: AsyncClient, test_garden: Garden):
    response = await client.delete(f"/api/v1/gardens/{test_garden.slug}/notes/{uuid.uuid4()}")
    assert response.status_code == 404


async def test_note_appears_on_garden(client: AsyncClient, test_garden: Garden):
    await client.post(f"/api/v1/gardens/{test_garden.slug}/notes", json={"note": "Visible on garden"})
    response = await client.get(f"/api/v1/gardens/{test_garden.slug}")
    assert response.status_code == 200
    notes = response.json()["notes"]
    assert any(n["note"] == "Visible on garden" for n in notes)


async def test_member_can_add_garden_note(member_client: AsyncClient, test_garden: Garden):
    response = await member_client.post(
        f"/api/v1/gardens/{test_garden.slug}/notes",
        json={"note": "Added by member"},
    )
    assert response.status_code == 201
    assert response.json()["note"] == "Added by member"


async def test_member_can_update_garden_note(member_client: AsyncClient, test_garden: Garden):
    create = await member_client.post(
        f"/api/v1/gardens/{test_garden.slug}/notes",
        json={"note": "Original"},
    )
    note_id = create.json()["id"]

    response = await member_client.patch(
        f"/api/v1/gardens/{test_garden.slug}/notes/{note_id}",
        json={"note": "Updated by member"},
    )
    assert response.status_code == 200
    assert response.json()["note"] == "Updated by member"


async def test_member_can_delete_garden_note(member_client: AsyncClient, test_garden: Garden):
    create = await member_client.post(
        f"/api/v1/gardens/{test_garden.slug}/notes",
        json={"note": "To be deleted by member"},
    )
    note_id = create.json()["id"]

    response = await member_client.delete(f"/api/v1/gardens/{test_garden.slug}/notes/{note_id}")
    assert response.status_code == 204


async def test_non_member_cannot_add_garden_note(second_client: AsyncClient, test_garden: Garden):
    response = await second_client.post(
        f"/api/v1/gardens/{test_garden.slug}/notes",
        json={"note": "Sneaky note"},
    )
    assert response.status_code == 403


async def test_unauthenticated_cannot_add_garden_note(unauthed_client: AsyncClient, test_garden: Garden):
    response = await unauthed_client.post(
        f"/api/v1/gardens/{test_garden.slug}/notes",
        json={"note": "No auth"},
    )
    assert response.status_code == 401
