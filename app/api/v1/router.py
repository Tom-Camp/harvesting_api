from fastapi import APIRouter

from app.api.v1 import admin, auth, feedback, garden, harvests, invitations, members, notes, plants, users

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(garden.router)
router.include_router(plants.router)
router.include_router(notes.router)
router.include_router(harvests.router)
router.include_router(members.router)
router.include_router(invitations.router)
router.include_router(admin.router)
router.include_router(feedback.router)
