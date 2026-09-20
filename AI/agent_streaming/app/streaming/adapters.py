from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Awaitable, Callable

import anyio
from sse_starlette import EventSourceResponse, ServerSentEvent
from sse_starlette.sse import SendTimeoutError
from starlette.responses import StreamingResponse

from app.domain.events import StreamEvent
from app.streaming.framing import encode_comment, encode_sse

SSE_HEADERS = {
    "Cache-Control": "no-store",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


class StreamingSendTimeout(RuntimeError):
    """The client did not accept an ASGI response chunk before the deadline."""


class _TimedStreamingResponse(StreamingResponse):
    def __init__(self, *args, send_timeout_seconds: float, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._send_timeout_seconds = send_timeout_seconds

    async def stream_response(self, send) -> None:
        async def timed_send(message) -> None:
            try:
                async with asyncio.timeout(self._send_timeout_seconds):
                    await send(message)
            except TimeoutError as exc:
                raise StreamingSendTimeout("SSE send timed out") from exc

        await timed_send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        async for chunk in self.body_iterator:
            if not isinstance(chunk, bytes | memoryview):
                chunk = chunk.encode(self.charset)
            await timed_send(
                {
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True,
                }
            )
        await timed_send({"type": "http.response.body", "body": b"", "more_body": False})


async def _with_heartbeat(
    source: AsyncIterator[StreamEvent], heartbeat_seconds: float
) -> AsyncIterator[bytes]:
    iterator = source.__aiter__()
    pending: asyncio.Task | None = None
    try:
        while True:
            if pending is None:
                pending = asyncio.create_task(anext(iterator))
            done, _ = await asyncio.wait({pending}, timeout=heartbeat_seconds)
            if not done:
                yield encode_comment("ping")
                continue
            try:
                event = pending.result()
            except StopAsyncIteration:
                break
            finally:
                pending = None
            yield encode_sse(event)
    finally:
        if pending is not None and not pending.done():
            pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)
        close = getattr(iterator, "aclose", None)
        if close is not None:
            await close()


class StreamingResponseAdapter:
    def __init__(self, *, heartbeat_seconds: float, send_timeout_seconds: float) -> None:
        self._heartbeat_seconds = heartbeat_seconds
        self._send_timeout_seconds = send_timeout_seconds

    def create(self, source: AsyncIterator[StreamEvent]) -> StreamingResponse:
        return _TimedStreamingResponse(
            _with_heartbeat(source, self._heartbeat_seconds),
            send_timeout_seconds=self._send_timeout_seconds,
            media_type="text/event-stream",
            headers=SSE_HEADERS,
        )


class _ManagedEventSourceResponse(EventSourceResponse):
    """Own cleanup even when a disconnect happens while send() is suspended."""

    def __init__(self, *args, source, on_close, **kwargs):
        super().__init__(*args, **kwargs)
        self._source = source
        self._on_close = on_close

    async def __call__(self, scope, receive, send):
        async def timed_send(message):
            # sse-starlette's body/ping timeout does not cover response headers
            # or the final empty body. Bound those sends as well.
            with anyio.move_on_after(self.send_timeout) as cancel_scope:
                await send(message)
            if cancel_scope.cancel_called:
                raise SendTimeoutError()

        try:
            await super().__call__(scope, receive, timed_send)
        finally:
            # Task-group cancellation must not interrupt asynchronous cleanup.
            with anyio.CancelScope(shield=True):
                try:
                    await self.body_iterator.aclose()
                finally:
                    try:
                        close = getattr(self._source, "aclose", None)
                        if close is not None:
                            await close()
                    finally:
                        if self._on_close is not None:
                            await self._on_close()


class EventSourceResponseAdapter:
    def __init__(self, *, heartbeat_seconds: float, send_timeout_seconds: float) -> None:
        self._heartbeat_seconds = heartbeat_seconds
        self._send_timeout_seconds = send_timeout_seconds

    def create(
        self, source: AsyncIterator[StreamEvent], *,
        on_close: Callable[[], Awaitable[None]] | None = None,
    ) -> EventSourceResponse:
        async def encoded_events():
            async for event in source:
                data = json.dumps(event.payload(), ensure_ascii=False, separators=(",", ":"))
                yield ServerSentEvent(
                    data=data,
                    event=event.event_type.value,
                    id=event.event_id,
                    sep="\n",
                )

        return _ManagedEventSourceResponse(
            encoded_events(),
            source=source,
            on_close=on_close,
            ping=self._heartbeat_seconds,
            send_timeout=self._send_timeout_seconds,
            headers=SSE_HEADERS,
            sep="\n",
        )
