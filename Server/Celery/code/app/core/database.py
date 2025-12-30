from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings

# Factory function for dependency injection
def create_session_factory(db_url: str):
    # Use NullPool to ensure connections are not shared across asyncio loops (crucial for Celery asyncio.run)
    engine = create_async_engine(db_url, echo=True, poolclass=NullPool)
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

# Keeping globals for backward compatibility/imports
# We default to NullPool here too to be safe with Celery tasks if they fallback to global
engine = create_async_engine(settings.DATABASE_URL, echo=True, poolclass=NullPool)
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

class Base(AsyncAttrs, DeclarativeBase):
    pass

async def get_db():
    async with async_session_factory() as session:
        yield session
