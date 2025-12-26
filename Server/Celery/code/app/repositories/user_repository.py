from typing import Callable
from contextlib import AbstractAsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]):
        self.session_factory = session_factory

    async def get_by_id(self, user_id: int) -> User:
        async with self.session_factory() as session:
            result = await session.execute(select(User).filter(User.id == user_id))
            return result.scalars().first()

    async def create_user(self, email: str, password: str) -> User:
        async with self.session_factory() as session:
            user = User(email=email, hashed_password=password)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
