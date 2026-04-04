from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI

from app.api.v1.router import router
from app.db import engine
from app.middleware import RequestLoggingMiddleware
from app.utils.config import settings
from app.utils.logging import configure_logging

configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("startup")
    yield
    await engine.dispose()
    logger.info("shutdown")


app = FastAPI(title="Harvest Food", version="0.1.0", lifespan=lifespan)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(router)
