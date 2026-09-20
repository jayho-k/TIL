from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID, uuid4

from sqlalchemy import update

from app.domain.models import RunStatus, Transport
from app.persistence.orm import ChatMessageRow, ChatRunRow


class RunRepository(Protocol):
    async def start_run(
        self,
        *,
        run_id: UUID,
        thread_id: str,
        transport: Transport,
        model: str,
        user_message: str,
    ) -> None: ...

    async def complete_run(
        self,
        *,
        run_id: UUID,
        thread_id: str,
        assistant_message: str,
        latency_ms: int,
    ) -> None: ...

    async def fail_run(
        self, *, run_id: UUID, error_code: str, error_message: str
    ) -> None: ...


class SqlAlchemyRunRepository:
    def __init__(self, session_factory, *, max_error_message_length: int) -> None:
        self._session_factory = session_factory
        self._max_error_message_length = max_error_message_length

    async def start_run(
        self,
        *,
        run_id: UUID,
        thread_id: str,
        transport: Transport,
        model: str,
        user_message: str,
    ) -> None:
        async with self._session_factory.begin() as session:
            session.add(
                ChatRunRow(
                    id=run_id,
                    thread_id=thread_id,
                    transport=transport.value,
                    status=RunStatus.RUNNING.value,
                    model=model,
                    input_chars=len(user_message),
                )
            )
            await session.flush()
            session.add(
                ChatMessageRow(
                    id=uuid4(),
                    run_id=run_id,
                    thread_id=thread_id,
                    role="user",
                    content=user_message,
                )
            )

    async def complete_run(
        self,
        *,
        run_id: UUID,
        thread_id: str,
        assistant_message: str,
        latency_ms: int,
    ) -> None:
        async with self._session_factory.begin() as session:
            session.add(
                ChatMessageRow(
                    id=uuid4(),
                    run_id=run_id,
                    thread_id=thread_id,
                    role="assistant",
                    content=assistant_message,
                )
            )
            await session.execute(
                update(ChatRunRow)
                .where(ChatRunRow.id == run_id)
                .values(
                    status=RunStatus.COMPLETED.value,
                    completed_at=datetime.now(UTC),
                    latency_ms=latency_ms,
                    output_chars=len(assistant_message),
                )
            )

    async def fail_run(self, *, run_id: UUID, error_code: str, error_message: str) -> None:
        safe_message = error_message[: self._max_error_message_length]
        async with self._session_factory.begin() as session:
            await session.execute(
                update(ChatRunRow)
                .where(ChatRunRow.id == run_id)
                .values(
                    status=RunStatus.FAILED.value,
                    completed_at=datetime.now(UTC),
                    error_code=error_code,
                    error_message=safe_message,
                )
            )
