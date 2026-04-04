from fastapi import APIRouter

from app.api.v1 import garden, plants, users

router = APIRouter(prefix="/api/v1")
router.include_router(users.router)
router.include_router(garden.router)
router.include_router(plants.router)
