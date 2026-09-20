import json
from uuid import UUID

import httpx
import pytest

from app.api.main import create_app
from app.domain.events import PublicEventType, StreamEvent
from app.service.limits import ConcurrencyLimiter


class FakeService:
    async def stream(self, command):
        yield StreamEvent.create(
            event_type=PublicEventType.STREAM_STARTED,
            run_id=command.run_id,
            thread_id=command.thread_id,
            sequence=0,
            data={"transport": command.transport.value},
        )
        yield StreamEvent.create(
            event_type=PublicEventType.MESSAGE_DELTA,
            run_id=command.run_id,
            thread_id=command.thread_id,
            sequence=1,
            data={"text": "hello"},
        )


def parse_events(body: str) -> list[tuple[str, dict]]:
    parsed = []
    for block in body.strip().split("\n\n"):
        fields = {}
        for line in block.splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                fields.setdefault(key, []).append(value)
        if "event" in fields:
            parsed.append((fields["event"][0], json.loads("\n".join(fields["data"]))))
    return parsed


@pytest.mark.asyncio
async def test_both_chat_routes_share_application_contract() -> None:
    app = create_app(service=FakeService(), readiness=lambda: True)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/v1/chat/streaming-response",
            json={"thread_id": "thread-1", "message": "hi"},
        )
        second = await client.post(
            "/v1/chat/event-source-response",
            json={"thread_id": "thread-1", "message": "hi"},
        )
        metrics = await client.get("/metrics")

    assert first.status_code == second.status_code == 200
    assert first.headers["content-type"].startswith("text/event-stream")
    assert second.headers["content-type"].startswith("text/event-stream")
    first_events = parse_events(first.text)
    second_events = parse_events(second.text)
    assert [item[0] for item in first_events] == [item[0] for item in second_events]
    assert first_events[1][1]["data"] == second_events[1][1]["data"] == {"text": "hello"}
    assert UUID(first_events[0][1]["run_id"])
    assert "stream_duration_seconds_count" in metrics.text
    assert 'transport="event_source_response"' in metrics.text
    assert first_events[0][1]["data"]["transport"] == "event_source_response"


@pytest.mark.asyncio
async def test_request_validation_and_health() -> None:
    app = create_app(service=FakeService(), readiness=lambda: True)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        invalid = await client.post(
            "/v1/chat/streaming-response", json={"thread_id": "", "message": ""}
        )
        live = await client.get("/health/live")
        ready = await client.get("/health/ready")
        metrics = await client.get("/metrics")

    assert invalid.status_code == 422
    assert live.json() == {"status": "ok"}
    assert ready.json() == {"status": "ready"}
    assert "active_sse_connections" in metrics.text
    assert "active_agent_runs" in metrics.text


@pytest.mark.asyncio
async def test_connection_capacity_is_rejected_before_stream_starts() -> None:
    limiter = ConcurrencyLimiter(capacity=1, timeout_seconds=0.01)
    await limiter.acquire()
    app = create_app(service=FakeService(), readiness=lambda: True, connection_limiter=limiter)
    try:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/v1/chat/streaming-response",
                json={"thread_id": "thread-1", "message": "hi"},
            )
    finally:
        limiter.release()

    assert response.status_code == 503
    assert response.headers["retry-after"] == "5"
