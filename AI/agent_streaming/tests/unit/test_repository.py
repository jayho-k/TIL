from contextlib import asynccontextmanager
from uuid import UUID

import pytest

from app.domain.models import Transport
from app.persistence.orm import ChatMessageRow, ChatRunRow
from app.persistence.repository import SqlAlchemyRunRepository


class FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.statements: list[object] = []
        self.operations: list[str] = []

    def add(self, value: object) -> None:
        self.added.append(value)
        self.operations.append(f"add:{type(value).__name__}")

    async def flush(self) -> None:
        self.operations.append("flush")

    async def execute(self, statement: object) -> None:
        self.statements.append(statement)


class FakeSessionFactory:
    def __init__(self) -> None:
        self.sessions: list[FakeSession] = []
        self.active = 0

    @asynccontextmanager
    async def begin(self):
        session = FakeSession()
        self.sessions.append(session)
        self.active += 1
        try:
            yield session
        finally:
            self.active -= 1


@pytest.mark.asyncio
async def test_start_run_writes_run_and_user_message_in_one_transaction() -> None:
    factory = FakeSessionFactory()
    repository = SqlAlchemyRunRepository(factory, max_error_message_length=20)
    run_id = UUID(int=1)

    await repository.start_run(
        run_id=run_id,
        thread_id="thread-1",
        transport=Transport.STREAMING_RESPONSE,
        model="test-model",
        user_message="hello",
    )

    assert factory.active == 0
    assert len(factory.sessions) == 1
    assert [type(item) for item in factory.sessions[0].added] == [ChatRunRow, ChatMessageRow]
    run, message = factory.sessions[0].added
    assert run.id == run_id
    assert run.status == "RUNNING"
    assert message.content == "hello"
    assert factory.sessions[0].operations == ["add:ChatRunRow", "flush", "add:ChatMessageRow"]


@pytest.mark.asyncio
async def test_completion_and_failure_each_use_a_fresh_transaction() -> None:
    factory = FakeSessionFactory()
    repository = SqlAlchemyRunRepository(factory, max_error_message_length=5)
    run_id = UUID(int=2)

    await repository.complete_run(
        run_id=run_id,
        thread_id="thread-2",
        assistant_message="answer",
        latency_ms=100,
    )
    await repository.fail_run(run_id=run_id, error_code="MODEL", error_message="too-long")

    assert factory.active == 0
    assert len(factory.sessions) == 2
    assert isinstance(factory.sessions[0].added[0], ChatMessageRow)
    assert len(factory.sessions[0].statements) == 1
    assert len(factory.sessions[1].statements) == 1
    assert "too-l" in str(factory.sessions[1].statements[0].compile().params)
