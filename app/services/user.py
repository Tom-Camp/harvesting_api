from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(session: AsyncSession, data: UserCreate) -> User:
    # TODO: hash password when auth is implemented
    user = User(email=data.email, hashed_password=data.password, location=data.location)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def update_user(session: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.location is not None:
        user.location = data.location
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
