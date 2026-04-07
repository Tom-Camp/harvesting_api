import uuid

import structlog
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.passwords import hash_password, verify_password
from app.models.user import User, UserRole, UserStatus
from app.utils.config import settings

logger = structlog.get_logger()


def _maybe_bootstrap_admin(user: User) -> None:
    """Promote to admin + active if email matches ADMIN_EMAIL env var."""
    if settings.admin_email and user.email.lower() == settings.admin_email.lower():
        user.status = UserStatus.ACTIVE
        user.role = UserRole.ADMIN



async def create_user(
    session: AsyncSession,
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
    )
    _maybe_bootstrap_admin(user)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate(session: AsyncSession, email: str, password: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def get_user(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)


async def update_user(session: AsyncSession, user: User, data) -> User:
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def approve_user(session: AsyncSession, user: User) -> User:
    user.status = UserStatus.ACTIVE
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def suspend_user(session: AsyncSession, user: User) -> User:
    user.status = UserStatus.SUSPENDED
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def set_role(session: AsyncSession, user: User, role: UserRole) -> User:
    user.role = role
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def ensure_admin(session: AsyncSession, email: str) -> None:
    """Startup bootstrap: promote the admin_email user if they already exist."""
    try:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user and (user.status != UserStatus.ACTIVE or user.role != UserRole.ADMIN):
            user.status = UserStatus.ACTIVE
            user.role = UserRole.ADMIN
            session.add(user)
            await session.commit()
            logger.info("admin_bootstrapped", email=email)
    except SQLAlchemyError:
        logger.warning("admin_bootstrap_skipped", email=email)
