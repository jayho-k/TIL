import asyncio
import json
from contextlib import aclosing
from uuid import uuid4

import httpx
import pytest
from langchain_core.messages import AIMessageChunk
from sse_starlette import EventSourceResponse
from starlette.requests import Request

from app.api.main import create_app
from app.api.routes import event_source_response, streaming_response
from app.api.schemas import ChatRequest
from app.domain.events import PublicEventType
from app.domain.models import Transport
from app.service.chat import ChatCommand, ChatStreamService
from app.service.limits import ConcurrencyLimiter
from app.streaming.projector import StreamEventProjector


def raw(text="hello", *, ns=(), node="model", tags=()):
    return {
        "type": "messages", "ns": ns,
        "data": (AIMessageChunk(content=text), {"langgraph_node": node, "tags": tags}),
    }


class Repository:
    def __init__(self, *, fail_at=None):
        self.calls = []
        self.fail_at = fail_at

    async def start_run(self, **kwargs):
        self.calls.append("start")
        if self.fail_at == "start":
            raise RuntimeError("private DB credentials")

    async def complete_run(self, **kwargs):
        self.calls.append("complete")
        if self.fail_at == "complete":
            raise RuntimeError("private DB credentials")

    async def fail_run(self, **kwargs):
        self.calls.append("fail")
        if self.fail_at == "fail":
            raise RuntimeError("private DB credentials")


class Source:
    def __init__(self, *, delay=0, fail=False):
        self.delay = delay
        self.fail = fail
        self.closed = False
        self.tasks = set()

    async def stream(self, *args):
        try:
            self.tasks.add(asyncio.current_task())
            yield raw()
            await asyncio.sleep(self.delay)
            self.tasks.add(asyncio.current_task())
            if self.fail:
                raise RuntimeError("private provider error")
            yield raw("world")
        finally:
            await asyncio.sleep(0)
            self.closed = True


def build(*, repository=None, source=None, timeout=2, batch_delay=0.02):
    repository = repository or Repository()
    source = source or Source()
    limiter = ConcurrencyLimiter(capacity=1, timeout_seconds=0.01)
    service = ChatStreamService(
        source=source, projector=StreamEventProjector(), repository=repository,
        limiter=limiter, model_name="fake", timeout_seconds=timeout,
        token_batch_max_chars=128, token_batch_max_delay_seconds=batch_delay,
    )
    return service, repository, limiter, source


def command():
    return ChatCommand(uuid4(), "thread", "hi", Transport.EVENT_SOURCE_RESPONSE)


@pytest.mark.asyncio
async def test_completed_is_emitted_only_after_commit():
    service, repository, limiter, _ = build()
    async with aclosing(service.stream(command())) as stream:
        async for event in stream:
            if event.event_type == PublicEventType.STREAM_COMPLETED:
                assert repository.calls == ["start", "complete"]
                break
    assert limiter.active == 0


@pytest.mark.asyncio
async def test_commit_failure_has_one_error_terminal_and_unique_ids():
    service, _, _, _ = build(repository=Repository(fail_at="complete"))
    events = [event async for event in service.stream(command())]
    assert PublicEventType.STREAM_COMPLETED not in [e.event_type for e in events]
    assert events[-1].data["code"] == "PERSISTENCE_ERROR"
    assert len({e.event_id for e in events}) == len(events)


@pytest.mark.asyncio
async def test_error_is_sent_even_if_failure_log_cannot_be_saved():
    service, _, limiter, _ = build(repository=Repository(fail_at="fail"), source=Source(fail=True))
    events = [event async for event in service.stream(command())]
    assert events[-1].data == {"code": "AGENT_ERROR", "message": "Agent execution failed"}
    assert limiter.active == 0


@pytest.mark.asyncio
async def test_source_iterator_runs_in_one_task():
    service, _, _, source = build(source=Source(delay=0.04))
    _ = [event async for event in service.stream(command())]
    assert len(source.tasks) == 1
    assert source.closed


@pytest.mark.asyncio
async def test_source_cleanup_failure_is_not_misreported_as_agent_timeout():
    class BrokenIterator:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

        async def aclose(self):
            raise RuntimeError("cleanup failed")

    class BrokenSource:
        def stream(self, *args):
            return BrokenIterator()

    service, _, _, _ = build(source=BrokenSource(), timeout=0.1)
    events = [event async for event in service.stream(command())]
    assert events[-1].data["code"] == "AGENT_ERROR"


@pytest.mark.asyncio
async def test_cleanup_error_during_cancellation_cannot_block_on_full_queue():
    class FailingCleanupSource:
        async def stream(self, *args):
            try:
                for _ in range(10):
                    yield raw("x" * 128)
            finally:
                raise RuntimeError("cleanup failed")

    service, _, limiter, _ = build(source=FailingCleanupSource())
    stream = service.stream(command())
    await anext(stream)
    await anext(stream)
    await asyncio.sleep(0.03)
    await asyncio.wait_for(stream.aclose(), timeout=0.5)
    assert limiter.active == 0


@pytest.mark.asyncio
async def test_cancellation_during_preflight_releases_both_slots():
    entered = asyncio.Event()

    class BlockingRepository(Repository):
        async def start_run(self, **kwargs):
            entered.set()
            await asyncio.Event().wait()

    service, _, limiter, _ = build(repository=BlockingRepository())
    app = create_app(service=service)
    task = asyncio.create_task(event_source_response(
        Request({"type": "http", "app": app}), ChatRequest(thread_id="t", message="hi")
    ))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert app.state.connection_limiter.active == limiter.active == 0


@pytest.mark.asyncio
async def test_continuous_tokens_flush_before_source_finishes():
    class Trickle:
        finished = False

        async def stream(self, *args):
            for _ in range(50):
                yield raw("x")
                # Stay above Windows' ~15ms monotonic clock resolution.
                await asyncio.sleep(0.02)
            self.finished = True

    source = Trickle()
    service, _, _, _ = build(source=source, batch_delay=0.08)
    async with aclosing(service.stream(command())) as stream:
        await anext(stream)
        delta = await anext(stream)
        assert delta.event_type == PublicEventType.MESSAGE_DELTA
        assert not source.finished
        assert len(delta.data["text"]) < 50


@pytest.mark.parametrize("ns,node,tags", [
    (("tools:child",), "model", ()), ((), "summarizer", ()),
    ((), "model", ("nostream",)), ((), "model", ("private",)),
])
def test_internal_text_is_not_public(ns, node, tags):
    assert StreamEventProjector().project(raw("internal", ns=ns, node=node, tags=tags)) == ()


def test_text_blocks_are_supported_but_reasoning_is_not_exposed():
    event = raw([
        {"type": "reasoning", "reasoning": "private"},
        {"type": "text", "text": "public"},
    ])
    assert StreamEventProjector().project(event)[0].data == {"text": "public"}


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["stream", "streaming-response", "event-source-response"])
@pytest.mark.parametrize("failure", ["capacity", "start"])
async def test_preflight_failures_return_503_and_release_connection(path, failure):
    service, _, limiter, _ = build(repository=Repository(fail_at=failure))
    app = create_app(service=service)
    if failure == "capacity":
        await limiter.acquire()
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                f"/v1/chat/{path}", json={"thread_id": "t", "message": "hi"}
            )
        assert response.status_code == 503
        assert response.headers["retry-after"] == "5"
        assert "private" not in response.text
        assert app.state.connection_limiter.active == 0
    finally:
        if failure == "capacity":
            limiter.release()
    assert limiter.active == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("route", [streaming_response, event_source_response])
async def test_routes_use_event_source_and_prepare_before_headers(route):
    service, repo, limiter, _ = build()
    app = create_app(service=service)
    response = await route(
        Request({"type": "http", "app": app}), ChatRequest(thread_id="t", message="hi")
    )
    try:
        assert isinstance(response, EventSourceResponse)
        assert repo.calls == ["start"]
    finally:
        # Exercise the response's ownership even before the first body item.
        async def broken_send(message):
            raise OSError("connection lost")

        async def receive():
            await asyncio.Event().wait()

        with pytest.raises(OSError):
            await response({"type": "http"}, receive, broken_send)
    assert app.state.connection_limiter.active == limiter.active == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["body_timeout", "disconnect", "header_timeout"])
async def test_response_owns_cleanup_even_when_generator_is_suspended(failure):
    service, _, limiter, source = build(source=Source(delay=10))
    app = create_app(service=service, send_timeout_seconds=0.03, heartbeat_seconds=0.01)
    response = await event_source_response(
        Request({"type": "http", "app": app}), ChatRequest(thread_id="t", message="hi")
    )
    first_delta = asyncio.Event()

    async def send(message):
        if failure == "header_timeout" and message["type"] == "http.response.start":
            await asyncio.Event().wait()
        if b"message.delta" in message.get("body", b""):
            first_delta.set()
            await asyncio.Event().wait()

    async def receive():
        if failure == "disconnect":
            await first_delta.wait()
            return {"type": "http.disconnect"}
        await asyncio.Event().wait()

    try:
        await asyncio.wait_for(response({"type": "http"}, receive, send), timeout=1)
    except Exception as exc:
        assert failure != "disconnect"
        assert type(exc).__name__ == "SendTimeoutError"
    assert app.state.connection_limiter.active == limiter.active == 0
    if failure != "header_timeout":
        assert source.closed


@pytest.mark.asyncio
async def test_agent_timeout_after_first_delta_is_public_and_cleans_source():
    service, _, limiter, source = build(source=Source(delay=10), timeout=0.1)
    app = create_app(service=service)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/chat/event-source-response", json={"thread_id": "t", "message": "hi"}
        )
    assert "message.delta" in response.text
    assert "AGENT_TIMEOUT" in response.text
    assert "stream.completed" not in response.text
    assert source.closed
    assert app.state.connection_limiter.active == limiter.active == 0
    payloads = [json.loads(line[6:]) for line in response.text.splitlines()
                if line.startswith("data: ")]
    assert len({p["event_id"] for p in payloads}) == len(payloads)
