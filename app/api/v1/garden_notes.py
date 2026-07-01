import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import GardenAccess, require_garden_member
from app.db import get_session
from app.schemas.garden import GardenNoteCreate, GardenNoteRead, GardenNoteUpdate
from app.services import garden as garden_service

router = APIRouter(prefix="/gardens/{slug}/notes", tags=["garden-notes"])


@router.get("", response_model=list[GardenNoteRead])
async def list_garden_notes(
    access: GardenAccess = Depends(require_garden_member),
) -> list[GardenNoteRead]:
    return [GardenNoteRead.model_validate(n) for n in access.garden.notes]


@router.post("", response_model=GardenNoteRead, status_code=status.HTTP_201_CREATED)
async def add_garden_note(
    data: GardenNoteCreate,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> GardenNoteRead:
    note = await garden_service.create_garden_note(session=session, garden_id=access.garden.id, data=data)
    return GardenNoteRead.model_validate(note)


@router.get("/{note_id}", response_model=GardenNoteRead)
async def get_garden_note(
    note_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> GardenNoteRead:
    note = await garden_service.get_garden_note(session, note_id)
    if not note or note.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return GardenNoteRead.model_validate(note)


@router.patch("/{note_id}", response_model=GardenNoteRead)
async def update_garden_note(
    note_id: uuid.UUID,
    data: GardenNoteUpdate,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> GardenNoteRead:
    note = await garden_service.get_garden_note(session, note_id)
    if not note or note.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    note = await garden_service.update_garden_note(session, note, data)
    return GardenNoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_garden_note(
    note_id: uuid.UUID,
    access: GardenAccess = Depends(require_garden_member),
    session: AsyncSession = Depends(get_session),
) -> None:
    note = await garden_service.get_garden_note(session, note_id)
    if not note or note.garden_id != access.garden.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    await garden_service.delete_garden_note(session, note)
