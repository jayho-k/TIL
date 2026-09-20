import json
from uuid import UUID

from app.domain.events import PublicEventType, StreamEvent
from app.streaming.framing import encode_comment, encode_sse


def make_event() -> StreamEvent:
    return StreamEvent.create(
        event_type=PublicEventType.MESSAGE_DELTA,
        run_id=UUID(int=1),
        thread_id="thread-1",
        sequence=1,
        data={"text": "안녕\nworld"},
    )


def test_sse_framing_is_utf8_json_with_one_delimiter() -> None:
    framed = encode_sse(make_event()).decode("utf-8")

    assert framed.startswith(f"id: {UUID(int=1)}:1\nevent: message.delta\n")
    assert framed.endswith("\n\n")
    assert not framed.endswith("\n\n\n")
    data_lines = [line[6:] for line in framed.splitlines() if line.startswith("data: ")]
    payload = json.loads("\n".join(data_lines))
    assert payload["data"] == {"text": "안녕\nworld"}


def test_comment_framing_strips_newlines() -> None:
    assert encode_comment("ping\r\ninjected") == b": pinginjected\n\n"
