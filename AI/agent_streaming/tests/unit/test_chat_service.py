import asyncio
from uuid import UUID

import pytest
from langchain_core.messages import AIMessageChunk

from app.domain.events import PublicEventType
from app.domain.models import Transport
from app.observability.metrics import Metrics
from app.service.chat import ChatCommand, ChatStreamService
from app.service.limits import ConcurrencyLimiter
from app.streaming.projector import StreamEventProjector


class FakeSource:
    def __init__(self, *, fail: Exception | None = None) -> None:
        self.fail = fail
        self.cancelled = False

    async def stream(self, message: str, thread_id: str):
        try:
            yield {"type": "messages", "ns": (), "data": (
                AIMessageChunk(content="hello "), {"langgraph_node": "model"},
            )}
            yield {"type": "messages", "ns": (), "data": (
                AIMessageChunk(content="world"), {"langgraph_node": "model"},
            )}
            if self.fail:
                raise self.fail
        except asyncio.CancelledError:
            self.cancelled = True
            raise


class FakeRepository:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def start_run(self, **kwargs) -> None:
        self.calls.append(("start", kwargs))

    async def complete_run(self, **kwargs) -> None:
        self.calls.append(("complete", kwargs))

    async def fail_run(self, **kwargs) -> None:
        self.calls.append(("fail", kwargs))


def command() -> ChatCommand:
    return ChatCommand(
        run_id=UUID(int=1),
        thread_id="thread-1",
        message="question",
        transport=Transport.STREAMING_RESPONSE,
    )


@pytest.mark.asyncio
async def test_service_shares_run_lifecycle_and_accumulates_answer() -> None:
    repository = FakeRepository()
    metrics = Metrics()
    service = ChatStreamService(
        source=FakeSource(),
        projector=StreamEventProjector(),
        repository=repository,
        limiter=ConcurrencyLimiter(capacity=1, timeout_seconds=0.1),
        model_name="model",
        timeout_seconds=1,
        metrics=metrics,
    )

    events = [event async for event in service.stream(command())]

    assert [event.event_type for event in events] == [
        PublicEventType.STREAM_STARTED,
        PublicEventType.MESSAGE_DELTA,
        PublicEventType.STREAM_COMPLETED,
    ]
    assert events[1].data == {"text": "hello world"}
    assert [name for name, _ in repository.calls] == ["start", "complete"]
    assert repository.calls[-1][1]["assistant_message"] == "hello world"
    assert metrics.active_agent_runs._value.get() == 0


@pytest.mark.asyncio
async def test_service_records_and_streams_safe_error() -> None:
    repository = FakeRepository()
    service = ChatStreamService(
        source=FakeSource(fail=RuntimeError("provider secret")),
        projector=StreamEventProjector(),
        repository=repository,
        limiter=ConcurrencyLimiter(capacity=1, timeout_seconds=0.1),
        model_name="model",
        timeout_seconds=1,
    )

    events = [event async for event in service.stream(command())]

    assert events[-1].event_type is PublicEventType.STREAM_ERROR
    assert events[-1].data == {"code": "AGENT_ERROR", "message": "Agent execution failed"}
    assert [name for name, _ in repository.calls] == ["start", "fail"]


@pytest.mark.asyncio
async def test_disconnect_cancellation_leaves_run_as_running_log() -> None:
    class BlockingSource:
        async def stream(self, message: str, thread_id: str):
            await asyncio.Event().wait()
            yield None

    repository = FakeRepository()
    limiter = ConcurrencyLimiter(capacity=1, timeout_seconds=0.1)
    service = ChatStreamService(
        source=BlockingSource(),
        projector=StreamEventProjector(),
        repository=repository,
        limiter=limiter,
        model_name="model",
        timeout_seconds=10,
    )
    stream = service.stream(command())
    assert (await anext(stream)).event_type is PublicEventType.STREAM_STARTED
    pending = asyncio.create_task(anext(stream))
    await asyncio.sleep(0)
    pending.cancel()

    with pytest.raises(asyncio.CancelledError):
        await pending
    await stream.aclose()

    assert [name for name, _ in repository.calls] == ["start"]
    assert limiter.active == 0


@pytest.mark.asyncio
async def test_token_batch_flushes_on_deadline_while_source_is_idle() -> None:
    class PausingSource:
        async def stream(self, message: str, thread_id: str):
            yield {"type": "messages", "ns": (), "data": (
                AIMessageChunk(content="first"), {"langgraph_node": "model"},
            )}
            await asyncio.sleep(1)
            yield {"type": "messages", "ns": (), "data": (
                AIMessageChunk(content="second"), {"langgraph_node": "model"},
            )}

    service = ChatStreamService(
        source=PausingSource(),
        projector=StreamEventProjector(),
        repository=FakeRepository(),
        limiter=ConcurrencyLimiter(capacity=1, timeout_seconds=0.1),
        model_name="model",
        timeout_seconds=2,
        token_batch_max_chars=128,
        token_batch_max_delay_seconds=0.01,
    )
    stream = service.stream(command())
    await anext(stream)

    event = await asyncio.wait_for(anext(stream), timeout=0.1)
    await stream.aclose()

    assert event.event_type is PublicEventType.MESSAGE_DELTA
    assert event.data == {"text": "first"}
