import os

import pytest
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import Settings

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_POSTGRES_TESTS") != "1", reason="RUN_POSTGRES_TESTS=1 required"
)


@pytest.mark.asyncio
async def test_migration_creates_chat_schema() -> None:
    engine = create_async_engine(Settings().postgres_dsn)
    try:
        async with engine.connect() as connection:
            tables = await connection.run_sync(lambda sync: set(inspect(sync).get_table_names()))
    finally:
        await engine.dispose()

    assert {"alembic_version", "chat_runs", "chat_messages"} <= tables
