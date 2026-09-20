import json
from dataclasses import dataclass
from time import perf_counter, sleep


@dataclass(slots=True)
class StreamStats:
    first_event_ms: float | None = None
    first_token_ms: float | None = None
    duration_ms: float = 0.0
    events: int = 0
    bytes_read: int = 0
    terminal_event: str | None = None


def consume_sse(
    response, *, slow_delay: float = 0.0, started_at: float | None = None,
) -> StreamStats:
    started = perf_counter() if started_at is None else started_at
    stats = StreamStats()
    event_name = None
    data_lines: list[str] = []
    for raw in response.iter_lines():
        if isinstance(raw, bytes):
            stats.bytes_read += len(raw)
            raw = raw.decode("utf-8")
        else:
            stats.bytes_read += len(raw.encode())
        if slow_delay:
            sleep(slow_delay)
        if raw.startswith("event: "):
            event_name = raw[7:]
        elif raw.startswith("data: "):
            data_lines.append(raw[6:])
        elif raw == "" and event_name:
            json.loads("\n".join(data_lines))
            if stats.first_event_ms is None:
                stats.first_event_ms = (perf_counter() - started) * 1000
            if event_name == "message.delta" and stats.first_token_ms is None:
                stats.first_token_ms = (perf_counter() - started) * 1000
            stats.events += 1
            if event_name in {"stream.completed", "stream.error"}:
                stats.terminal_event = event_name
            event_name = None
            data_lines.clear()
    stats.duration_ms = (perf_counter() - started) * 1000
    return stats
