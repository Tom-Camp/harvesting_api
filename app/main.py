from fastapi import FastAPI

from app.api.v1.router import router
from app.middleware import RequestLoggingMiddleware
from app.utils.config import settings
from app.utils.logging import configure_logging

configure_logging(log_level=settings.log_level, json_logs=settings.json_logs)

app = FastAPI(title="Harvest Food", version="0.1.0")
app.add_middleware(RequestLoggingMiddleware)
app.include_router(router)
