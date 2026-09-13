import json
from typing import Any


def sse_event(event: str, payload: dict[str, Any]) -> dict[str, str]:
    public = {key: value for key, value in payload.items() if key != "thread_id"}
    return {"event": event, "data": json.dumps(public, ensure_ascii=False)}
