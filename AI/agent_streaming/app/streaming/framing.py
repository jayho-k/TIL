import json

from app.domain.events import StreamEvent


def _sanitize_field(value: str) -> str:
    return value.replace("\r", "").replace("\n", "")


def encode_sse(event: StreamEvent) -> bytes:
    payload = json.dumps(event.payload(), ensure_ascii=False, separators=(",", ":"))
    lines = [
        f"id: {_sanitize_field(event.event_id)}",
        f"event: {_sanitize_field(event.event_type.value)}",
    ]
    lines.extend(f"data: {line}" for line in payload.splitlines() or [""])
    return ("\n".join(lines) + "\n\n").encode("utf-8")


def encode_comment(comment: str) -> bytes:
    return f": {_sanitize_field(comment)}\n\n".encode()
