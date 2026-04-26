import os

os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
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

from app.auth.dependencies import get_current_user, require_active_user
from app.db import get_session
from app.main import app
from app.models.garden import Garden  # noqa: F401
from app.models.garden_member import GardenMember, GardenMemberRole  # noqa: F401
from app.models.plant import Plant  # noqa: F401
from app.models.user import User, UserRole, UserStatus  # noqa: F401

_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
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
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        status=UserStatus.ACTIVE,
        role=UserRole.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    session.expunge(user)
    return user


@pytest_asyncio.fixture
async def admin_user(session: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        first_name="Admin",
        status=UserStatus.ACTIVE,
        role=UserRole.ADMIN,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    session.expunge(user)
    return user


@pytest_asyncio.fixture
async def pending_user(session: AsyncSession) -> User:
    user = User(
        email="pending@example.com",
        first_name="Pending",
        status=UserStatus.PENDING,
        role=UserRole.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    session.expunge(user)
    return user


@pytest_asyncio.fixture
async def second_user(session: AsyncSession) -> User:
    user = User(
        email="second@example.com",
        first_name="Second",
        status=UserStatus.ACTIVE,
        role=UserRole.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    session.expunge(user)
    return user


@pytest_asyncio.fixture
async def test_garden(session: AsyncSession, test_user: User) -> Garden:
    garden = Garden(user_id=test_user.id, name="My Test Garden", slug="my-test-garden", location="Austin, TX")
    session.add(garden)
    await session.flush()
    session.add(GardenMember(garden_id=garden.id, user_id=test_user.id, role=GardenMemberRole.OWNER))
    await session.commit()
    await session.refresh(garden)
    session.expunge(garden)
    return garden


@pytest_asyncio.fixture
async def test_plant(session: AsyncSession, test_garden: Garden) -> Plant:
    plant = Plant(garden_id=test_garden.id, plant_type="vegetable", species="tomato", variety="cherry")
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
    async def override_auth():
        return test_user

    app.dependency_overrides[get_session] = _session_override(engine)
    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[require_active_user] = override_auth
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_client(engine, admin_user: User) -> AsyncGenerator[AsyncClient, None]:
    async def override_auth():
        return admin_user

    app.dependency_overrides[get_session] = _session_override(engine)
    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[require_active_user] = override_auth
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def second_client(engine, second_user: User) -> AsyncGenerator[AsyncClient, None]:
    async def override_auth():
        return second_user

    app.dependency_overrides[get_session] = _session_override(engine)
    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[require_active_user] = override_auth
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def pending_client(engine, pending_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Client for a user whose account is pending approval — require_active_user NOT overridden."""

    async def override_get_current_user():
        return pending_user

    app.dependency_overrides[get_session] = _session_override(engine)
    app.dependency_overrides[get_current_user] = override_get_current_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def member_client(
    engine, session: AsyncSession, second_user: User, test_garden: Garden
) -> AsyncGenerator[AsyncClient, None]:
    """Client for second_user as an explicit MEMBER (not owner) of test_garden."""
    session.add(GardenMember(garden_id=test_garden.id, user_id=second_user.id, role=GardenMemberRole.MEMBER))
    await session.commit()

    async def override_auth():
        return second_user

    app.dependency_overrides[get_session] = _session_override(engine)
    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[require_active_user] = override_auth
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthed_client(engine) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_session] = _session_override(engine)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
