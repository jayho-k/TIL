import asyncio
from uuid import UUID

import pytest

from app.domain.events import PublicEventType, StreamEvent
from app.streaming.adapters import (
    EventSourceResponseAdapter,
    StreamingResponseAdapter,
    StreamingSendTimeout,
    _with_heartbeat,
)


def events(event: StreamEvent):
    async def generate():
        yield event

    return generate()


async def render(response) -> tuple[dict, bytes]:
    messages = []

    async def send(message):
        messages.append(message)

    async def receive():
        await asyncio.Event().wait()

    await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, send)
    start = next(message for message in messages if message["type"] == "http.response.start")
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return start, body


@pytest.mark.asyncio
async def test_adapters_emit_equivalent_application_events_and_headers() -> None:
    streaming = StreamingResponseAdapter(heartbeat_seconds=15, send_timeout_seconds=30)
    event_source = EventSourceResponseAdapter(heartbeat_seconds=15, send_timeout_seconds=30)
    event = StreamEvent.create(
        event_type=PublicEventType.MESSAGE_DELTA,
        run_id=UUID(int=1),
        thread_id="thread-1",
        sequence=1,
        data={"text": "hello"},
    )

    streaming_start, streaming_body = await render(streaming.create(events(event)))
    event_start, event_body = await render(event_source.create(events(event)))

    assert streaming_body == event_body
    assert b"event: message.delta" in streaming_body
    for start in (streaming_start, event_start):
        headers = {key.lower(): value for key, value in start["headers"]}
        assert headers[b"content-type"].startswith(b"text/event-stream")
        assert headers[b"cache-control"] == b"no-store"
        assert headers[b"x-accel-buffering"] == b"no"


@pytest.mark.asyncio
async def test_streaming_response_emits_comment_while_source_is_idle() -> None:
    async def slow_source():
        await asyncio.sleep(1)
        yield StreamEvent.create(
            event_type=PublicEventType.STREAM_COMPLETED,
            run_id=UUID(int=1),
            thread_id="thread-1",
            sequence=1,
            data={},
        )

    stream = _with_heartbeat(slow_source(), heartbeat_seconds=0.01)
    try:
        assert await anext(stream) == b": ping\n\n"
    finally:
        await stream.aclose()


@pytest.mark.asyncio
async def test_streaming_response_times_out_blocked_send() -> None:
    response = StreamingResponseAdapter(
        heartbeat_seconds=15, send_timeout_seconds=0.01
    ).create(events(StreamEvent.create(
        event_type=PublicEventType.MESSAGE_DELTA,
        run_id=UUID(int=1), thread_id="thread-1", sequence=1, data={"text": "x"},
    )))

    async def blocked_send(_message):
        await asyncio.sleep(1)

    async def receive():
        await asyncio.Event().wait()

    with pytest.raises(StreamingSendTimeout):
        await response({"type": "http", "asgi": {"spec_version": "2.4"}}, receive, blocked_send)
