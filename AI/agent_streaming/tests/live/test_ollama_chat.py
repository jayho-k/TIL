import json
import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.main import app

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_TESTS") != "1", reason="RUN_LIVE_TESTS=1 required"
)


def collect_text(body: str) -> str:
    chunks = []
    for line in body.splitlines():
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            if payload["data"].get("text"):
                chunks.append(payload["data"]["text"])
    return "".join(chunks)


def test_two_transports_share_redis_multiturn_state() -> None:
    thread_id = str(uuid4())
    with TestClient(app) as client:
        first = client.post(
            "/v1/chat/streaming-response",
            json={"thread_id": thread_id, "message": "Remember cobalt. Reply OK."},
        )
        second = client.post(
            "/v1/chat/event-source-response",
            json={
                "thread_id": thread_id,
                "message": "What word did I ask you to remember? Reply with only that word.",
            },
        )

    assert first.status_code == second.status_code == 200
    assert "stream.completed" in first.text
    assert "stream.completed" in second.text
    assert "cobalt" in collect_text(second.text).lower()
