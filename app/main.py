from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.router import router
from app.auth.google import prefetch_jwks
from app.db import engine
from app.middleware import RequestLoggingMiddleware
from app.utils.config import settings
from app.utils.logging import configure_logging

configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await prefetch_jwks()
    logger.info("startup")
    yield
    await engine.dispose()
    logger.info("shutdown")


app = FastAPI(title="Harvest Food", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
