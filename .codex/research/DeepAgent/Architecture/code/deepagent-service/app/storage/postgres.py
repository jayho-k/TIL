from typing import Any


def create_postgres_engine(url: str, *, echo: bool = False) -> Any:
    """Create an async SQLAlchemy engine without leaking it into service code."""
    from sqlalchemy.ext.asyncio import create_async_engine

    return create_async_engine(url, echo=echo, pool_pre_ping=True)

