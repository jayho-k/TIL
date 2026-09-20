from datetime import UTC
from uuid import UUID

from app.domain.events import PublicEventType, StreamEvent


def test_stream_event_has_stable_envelope() -> None:
    event = StreamEvent.create(
        event_type=PublicEventType.MESSAGE_DELTA,
        run_id=UUID(int=1),
        thread_id="thread-1",
        sequence=2,
        data={"text": "안녕"},
    )

    payload = event.payload()

    assert payload["schema_version"] == "1"
    assert payload["event_id"] == f"{UUID(int=1)}:2"
    assert payload["run_id"] == str(UUID(int=1))
    assert payload["thread_id"] == "thread-1"
    assert payload["sequence"] == 2
    assert payload["data"] == {"text": "안녕"}
    assert event.timestamp.tzinfo is UTC


def test_stream_event_is_immutable() -> None:
    event = StreamEvent.create(
        event_type=PublicEventType.STREAM_STARTED,
        run_id=UUID(int=2),
        thread_id="thread-2",
        sequence=0,
        data={},
    )

    try:
        event.sequence = 3
    except Exception as exc:
        assert exc.__class__.__name__ == "ValidationError"
    else:
        raise AssertionError("StreamEvent must be immutable")
