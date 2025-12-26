from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Create Async Engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create Async Session Factory
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

class Base(AsyncAttrs, DeclarativeBase):
    pass

async def get_db():
    async with async_session_factory() as session:
        yield session
