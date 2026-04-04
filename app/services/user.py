from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.user import User


async def find_or_create_from_google(session: AsyncSession, claims: dict[str, str]) -> User:
    result = await session.execute(select(User).where(User.google_sub == claims["sub"]))
    user = result.scalar_one_or_none()
    if user:
        return user
    user = User(
        google_sub=claims["sub"],
        email=claims["email"],
        first_name=claims.get("given_name"),
        last_name=claims.get("family_name"),
        picture=claims.get("picture"),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def update_user(session: AsyncSession, user: User, location: str) -> User:
    user.location = location
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
