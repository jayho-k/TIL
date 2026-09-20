from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import aclosing, asynccontextmanager
from dataclasses import dataclass
from time import monotonic
from uuid import UUID

import anyio

from app.agents.source import AgentEventSource
from app.domain.events import PublicEventType, StreamEvent
from app.domain.models import Transport
from app.persistence.repository import RunRepository
from app.service.limits import ConcurrencyLimiter
from app.streaming.batching import TokenBatcher
from app.streaming.projector import ProjectedEvent, StreamEventProjector

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ChatCommand:
    run_id: UUID
    thread_id: str
    message: str
    transport: Transport


class ChatStreamService:
    def __init__(
        self,
        *,
        source: AgentEventSource,
        projector: StreamEventProjector,
        repository: RunRepository,
        limiter: ConcurrencyLimiter,
        model_name: str,
        timeout_seconds: float,
        token_batch_max_chars: int = 128,
        token_batch_max_delay_seconds: float = 0.02,
        persistence_timeout_seconds: float = 10,
        metrics=None,
    ) -> None:
        self._source = source
        self._projector = projector
        self._repository = repository
        self._limiter = limiter
        self._model_name = model_name
        self._timeout_seconds = timeout_seconds
        self._token_batch_max_chars = token_batch_max_chars
        self._token_batch_max_delay_seconds = token_batch_max_delay_seconds
        self._metrics = metrics
        self._persistence_timeout_seconds = persistence_timeout_seconds

    async def stream(self, command: ChatCommand) -> AsyncIterator[StreamEvent]:
        started = monotonic()
        sequence = 0
        answer: list[str] = []
        async with self._run_slot():
            async with asyncio.timeout(self._persistence_timeout_seconds):
                await self._repository.start_run(
                    run_id=command.run_id,
                    thread_id=command.thread_id,
                    transport=command.transport,
                    model=self._model_name,
                    user_message=command.message,
                )
            yield self._event(
                command,
                sequence,
                PublicEventType.STREAM_STARTED,
                {"transport": command.transport.value},
            )
            sequence += 1
            try:
                parts = self._batched_events(command.message, command.thread_id)
                async with aclosing(parts):
                    async for projected in parts:
                        if projected.event_type is PublicEventType.MESSAGE_DELTA:
                            answer.append(str(projected.data["text"]))
                        yield self._event(
                            command,
                            sequence,
                            projected.event_type,
                            projected.data,
                        )
                        sequence += 1
            except asyncio.CancelledError:
                raise
            except TimeoutError as exc:
                await self._record_failure(command, "AGENT_TIMEOUT", exc)
                yield self._event(
                    command,
                    sequence,
                    PublicEventType.STREAM_ERROR,
                    {"code": "AGENT_TIMEOUT", "message": "Agent execution timed out"},
                )
                return
            except Exception as exc:
                await self._record_failure(command, "AGENT_ERROR", exc)
                yield self._event(
                    command,
                    sequence,
                    PublicEventType.STREAM_ERROR,
                    {"code": "AGENT_ERROR", "message": "Agent execution failed"},
                )
                return

            latency_ms = int((monotonic() - started) * 1000)
            try:
                async with asyncio.timeout(self._persistence_timeout_seconds):
                    await self._repository.complete_run(
                        run_id=command.run_id,
                        thread_id=command.thread_id,
                        assistant_message="".join(answer),
                        latency_ms=latency_ms,
                    )
            except Exception as exc:
                await self._record_failure(command, "PERSISTENCE_ERROR", exc)
                yield self._event(command, sequence, PublicEventType.STREAM_ERROR, {
                    "code": "PERSISTENCE_ERROR", "message": "Could not save the response",
                })
                return
            yield self._event(command, sequence, PublicEventType.STREAM_COMPLETED, {
                "latency_ms": latency_ms, "output_chars": sum(map(len, answer)),
            })

    async def _record_failure(self, command: ChatCommand, code: str, exc: Exception) -> None:
        try:
            async with asyncio.timeout(self._persistence_timeout_seconds):
                await self._repository.fail_run(
                    run_id=command.run_id, error_code=code,
                    error_message=str(exc) or code,
                )
        except Exception:
            # Do not let a secondary DB failure suppress the public terminal event.
            # Avoid logging provider/DB exception text, which may contain credentials.
            logger.error("Failed to persist run failure: run_id=%s code=%s", command.run_id, code)

    @asynccontextmanager
    async def _run_slot(self):
        async with self._limiter.slot():
            if self._metrics is not None:
                self._metrics.active_agent_runs.inc()
            try:
                yield
            finally:
                if self._metrics is not None:
                    self._metrics.active_agent_runs.dec()

    async def _batched_events(
        self, message: str, thread_id: str
    ) -> AsyncIterator[ProjectedEvent]:
        # One task owns the entire source lifecycle, including its timeout contexts.
        queue: asyncio.Queue = asyncio.Queue(maxsize=1)
        finished = object()

        async def produce():
            try:
                iterator = self._source.stream(message, thread_id)
                try:
                    async for raw in iterator:
                        await queue.put(raw)
                finally:
                    with anyio.CancelScope(shield=True):
                        close = getattr(iterator, "aclose", None)
                        if close is not None:
                            await close()
            except Exception as exc:
                # The consumer has stopped during cancellation; attempting to
                # enqueue a cleanup error into its full queue would deadlock.
                if asyncio.current_task().cancelling():
                    logger.error("Agent source cleanup failed during cancellation")
                    raise
                await queue.put(exc)
            else:
                await queue.put(finished)

        producer = asyncio.create_task(produce(), name="agent-stream-source")
        batcher = TokenBatcher(
            max_chars=self._token_batch_max_chars,
            max_delay_seconds=self._token_batch_max_delay_seconds,
        )
        deadline = monotonic() + self._timeout_seconds
        try:
            while True:
                remaining = deadline - monotonic()
                if remaining <= 0:
                    raise TimeoutError("Agent execution timed out")
                if batcher.should_flush():
                    yield ProjectedEvent(
                        PublicEventType.MESSAGE_DELTA, {"text": batcher.flush()}
                    )
                    continue
                batch_remaining = batcher.remaining_seconds
                wait_seconds = (
                    min(remaining, batch_remaining) if batch_remaining is not None else remaining
                )
                try:
                    raw = await asyncio.wait_for(queue.get(), timeout=wait_seconds)
                except TimeoutError:
                    continue
                if raw is finished:
                    break
                if isinstance(raw, Exception):
                    raise raw
                for projected in self._projector.project(raw):
                    if projected.event_type is PublicEventType.MESSAGE_DELTA:
                        batcher.add(str(projected.data["text"]))
                        if batcher.should_flush():
                            yield ProjectedEvent(
                                PublicEventType.MESSAGE_DELTA,
                                {"text": batcher.flush()},
                            )
                        continue
                    if batcher.pending:
                        yield ProjectedEvent(
                            PublicEventType.MESSAGE_DELTA, {"text": batcher.flush()}
                        )
                    yield projected
            if batcher.pending:
                yield ProjectedEvent(
                    PublicEventType.MESSAGE_DELTA, {"text": batcher.flush()}
                )
        finally:
            with anyio.CancelScope(shield=True):
                if not producer.done():
                    producer.cancel()
                await asyncio.gather(producer, return_exceptions=True)

    @staticmethod
    def _event(
        command: ChatCommand,
        sequence: int,
        event_type: PublicEventType,
        data: dict,
    ) -> StreamEvent:
        return StreamEvent.create(
            event_type=event_type,
            run_id=command.run_id,
            thread_id=command.thread_id,
            sequence=sequence,
            data=data,
        )
