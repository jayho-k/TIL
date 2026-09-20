from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.config import Settings


def create_database(settings: Settings) -> tuple[AsyncEngine, async_sessionmaker]:
    engine = create_async_engine(
        settings.postgres_dsn,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout_seconds,
        pool_pre_ping=True,
    )
    return engine, async_sessionmaker(engine, expire_on_commit=False)
