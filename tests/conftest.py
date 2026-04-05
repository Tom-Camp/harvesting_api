import os

# Set required env vars before any app module is imported (Pydantic Settings reads on instantiation)
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-secret")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-at-least-32-chars-long!")

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.auth.dependencies import get_current_user, require_complete_profile
from app.db import get_session
from app.main import app
from app.models.garden import Garden  # noqa: F401 — registers table with SQLModel.metadata
from app.models.plant import Plant  # noqa: F401 — registers table with SQLModel.metadata
from app.models.user import User  # noqa: F401 — registers table with SQLModel.metadata

_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    """Fresh in-memory SQLite DB per test. StaticPool ensures all sessions share one connection."""
    _engine = create_async_engine(
        _TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield _engine
    await _engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    _Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with _Session() as s:
        yield s


@pytest_asyncio.fixture
async def test_user(session: AsyncSession) -> User:
    user = User(
        google_sub="google-sub-test-1",
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        location="Austin, TX",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    session.expunge(user)  # detach so endpoint sessions can adopt it freely
    return user


@pytest_asyncio.fixture
async def incomplete_user(session: AsyncSession) -> User:
    user = User(
        google_sub="google-sub-test-2",
        email="incomplete@example.com",
        first_name="Incomplete",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    session.expunge(user)
    return user


@pytest_asyncio.fixture
async def test_garden(session: AsyncSession, test_user: User) -> Garden:
    garden = Garden(user_id=test_user.id, name="My Test Garden")
    session.add(garden)
    await session.commit()
    await session.refresh(garden)
    session.expunge(garden)
    return garden


@pytest_asyncio.fixture
async def test_plant(session: AsyncSession, test_garden: Garden) -> Plant:
    plant = Plant(garden_id=test_garden.id, plant_type="tomato", variety="cherry")
    session.add(plant)
    await session.commit()
    await session.refresh(plant)
    session.expunge(plant)
    return plant


def _session_override(engine):
    _Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override():
        async with _Session() as s:
            yield s

    return override


@pytest_asyncio.fixture
async def client(engine, test_user: User) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client authenticated as a user with a complete profile."""

    async def override_auth():
        return test_user

    app.dependency_overrides[get_session] = _session_override(engine)
    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[require_complete_profile] = override_auth
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def incomplete_client(engine, incomplete_user: User) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client authenticated as a user without a location set.

    require_complete_profile is NOT overridden so it naturally raises 403.
    """

    async def override_get_current_user():
        return incomplete_user

    app.dependency_overrides[get_session] = _session_override(engine)
    app.dependency_overrides[get_current_user] = override_get_current_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthed_client(engine) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client with no auth overrides — used for testing auth endpoints."""
    app.dependency_overrides[get_session] = _session_override(engine)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
