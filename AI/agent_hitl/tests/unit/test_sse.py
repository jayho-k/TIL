import json

from app.api.sse import sse_event


def test_sse_event_serializes_json_without_thread_id():
    result = sse_event("progress", {"run_id": "r1", "thread_id": "secret", "stage": "start"})
    assert result["event"] == "progress"
    assert json.loads(result["data"]) == {"run_id": "r1", "stage": "start"}
