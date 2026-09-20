import inspect
import logging
from time import perf_counter
from uuid import uuid4

import anyio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.schemas import ChatRequest
from app.domain.models import Transport
from app.service.chat import ChatCommand
from app.service.limits import CapacityExceeded

router = APIRouter()
logger = logging.getLogger(__name__)


async def _stream(request: Request, payload: ChatRequest, transport: Transport):
    command = ChatCommand(
        run_id=uuid4(),
        thread_id=payload.thread_id,
        message=payload.message,
        transport=transport,
    )
    limiter = request.app.state.connection_limiter
    try:
        await limiter.acquire()
    except CapacityExceeded as exc:
        raise HTTPException(
            status_code=503,
            detail="stream capacity exhausted",
            headers={"Retry-After": "5"},
        ) from exc
    metrics = request.app.state.metrics
    metrics.active_sse_connections.labels(transport=transport.value).inc()
    started = perf_counter()
    status = "cancelled"
    stream = None
    released = False

    async def close():
        nonlocal released
        if released:
            return
        released = True
        try:
            if stream is not None:
                await stream.aclose()
        finally:
            metrics.stream_duration.labels(
                transport=transport.value,
                status=status,
            ).observe(perf_counter() - started)
            metrics.active_sse_connections.labels(transport=transport.value).dec()
            limiter.release()

    try:
        stream = request.app.state.chat_service.stream(command)
        # The first item is stream.started, after permit acquisition and DB commit.
        # No Agent execution or timeout context has started at this point.
        first = await anext(stream)

        def record(event):
            nonlocal status
            metrics.stream_events.labels(
                transport=transport.value, event=event.event_type.value,
            ).inc()
            if event.event_type.value == "stream.completed":
                status = "completed"
            elif event.event_type.value == "stream.error":
                status = "error"
            return event

        async def admitted_source():
            yield record(first)
            async for event in stream:
                yield record(event)

        adapter = request.app.state.response_adapters[Transport.EVENT_SOURCE_RESPONSE]
        response = adapter.create(admitted_source(), on_close=close)
    except BaseException as exc:
        status = "error" if isinstance(exc, Exception) else "cancelled"
        with anyio.CancelScope(shield=True):
            await close()
        if isinstance(exc, CapacityExceeded):
            raise HTTPException(
                status_code=503, detail="agent capacity exhausted",
                headers={"Retry-After": "5"},
            ) from exc
        if isinstance(exc, Exception):
            logger.error("Stream initialization failed: run_id=%s", command.run_id)
            raise HTTPException(
                status_code=503, detail="stream initialization unavailable",
                headers={"Retry-After": "5"},
            ) from exc
        raise
    return response


@router.post("/v1/chat/streaming-response", deprecated=True)
async def streaming_response(request: Request, payload: ChatRequest):
    return await _stream(request, payload, Transport.EVENT_SOURCE_RESPONSE)


@router.post("/v1/chat/stream")
@router.post("/v1/chat/event-source-response")
async def event_source_response(request: Request, payload: ChatRequest):
    return await _stream(request, payload, Transport.EVENT_SOURCE_RESPONSE)


@router.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def ready(request: Request) -> dict[str, str]:
    result = request.app.state.readiness()
    if inspect.isawaitable(result):
        result = await result
    if not result:
        raise HTTPException(status_code=503, detail="not ready")
    return {"status": "ready"}


@router.get("/metrics")
async def metrics(request: Request) -> Response:
    registry = getattr(request.app.state, "metrics_registry", None)
    return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
