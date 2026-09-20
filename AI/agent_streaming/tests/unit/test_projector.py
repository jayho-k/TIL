from langchain_core.messages import AIMessageChunk, HumanMessage

from app.domain.events import PublicEventType
from app.streaming.projector import StreamEventProjector


def test_projects_assistant_message_chunk() -> None:
    projector = StreamEventProjector()
    raw = {
        "type": "messages",
        "data": (AIMessageChunk(content="hello"), {"langgraph_node": "model"}),
        "ns": (),
    }

    projected = projector.project(raw)

    assert len(projected) == 1
    assert projected[0].event_type is PublicEventType.MESSAGE_DELTA
    assert projected[0].data == {"text": "hello"}


def test_ignores_non_assistant_empty_and_private_modes() -> None:
    projector = StreamEventProjector()

    assert projector.project({"type": "messages", "data": (HumanMessage("x"), {})}) == ()
    assert projector.project({"type": "messages", "data": (AIMessageChunk(content=""), {})}) == ()
    assert projector.project({"type": "values", "data": {"secret": "state"}}) == ()
    assert projector.project({"type": "debug", "data": {"prompt": "secret"}}) == ()


def test_projects_only_explicit_public_custom_events() -> None:
    projector = StreamEventProjector()

    projected = projector.project(
        {
            "type": "custom",
            "ns": (),
            "data": {"event": "tool.started", "data": {"name": "search"}, "public": True},
        }
    )

    assert projected[0].event_type is PublicEventType.TOOL_STARTED
    assert projected[0].data == {"name": "search"}
    assert projector.project(
        {"type": "custom", "ns": (), "data": {
            "event": "tool.started", "data": {}, "public": False,
        }}
    ) == ()


def test_malformed_events_are_ignored() -> None:
    projector = StreamEventProjector()

    assert projector.project(None) == ()
    assert projector.project({"type": "messages", "data": "wrong"}) == ()
    assert projector.project({"type": "custom", "data": {"public": True}}) == ()
