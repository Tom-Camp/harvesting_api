from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.auth.passwords import hash_password
from app.models.password_reset import PasswordResetToken
from app.models.user import User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_reset_token(session: AsyncSession, user: User) -> PasswordResetToken:
    token = PasswordResetToken(user_id=user.id)
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return token


async def get_valid_token(session: AsyncSession, token: str) -> PasswordResetToken | None:
    result = await session.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == token)
    )
    record = result.scalar_one_or_none()
    if not record:
        return None
    if record.used_at is not None:
        return None
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    return record


async def consume_token(session: AsyncSession, record: PasswordResetToken, new_password: str) -> None:
    result = await session.get(User, record.user_id)
    if result:
        result.password_hash = hash_password(new_password)
        session.add(result)
    record.used_at = datetime.now(timezone.utc)
    session.add(record)
    await session.commit()
