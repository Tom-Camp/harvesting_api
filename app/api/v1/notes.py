import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import GardenAccess, require_garden_member
from app.db import get_session
from app.schemas.plant import NoteCreate, NoteRead, NoteUpdate
from app.services import plant as plant_service

router = APIRouter(prefix="/gardens/{slug}/plants/{plant_id}/notes", tags=["notes"])


async def _get_plant_in_garden(
    plant_id: uuid.UUID,
    access: GardenAccess,
    session: AsyncSession,
):
    plant = await plant_service.get_plant(session, plant_id)
    if not plant or plant.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def add_note(
    plant_id: uuid.UUID,
    data: NoteCreate,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> NoteRead:
    await _get_plant_in_garden(plant_id, access, session)
    note = await plant_service.create_note(session=session, plant_id=plant_id, data=data)
    return NoteRead.model_validate(note)


@router.patch("/{note_id}", response_model=NoteRead)
async def update_note(
    plant_id: uuid.UUID,
    note_id: uuid.UUID,
    data: NoteUpdate,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> NoteRead:
    await _get_plant_in_garden(plant_id, access, session)
    note = await plant_service.get_note(session, note_id)
    if not note or note.plant_id != plant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    note = await plant_service.update_note(session, note, data)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    plant_id: uuid.UUID,
    note_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> None:
    await _get_plant_in_garden(plant_id, access, session)
    note = await plant_service.get_note(session, note_id)
    if not note or note.plant_id != plant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    await plant_service.delete_note(session, note)
