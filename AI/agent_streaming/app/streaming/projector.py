from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessageChunk

from app.domain.events import PublicEventType


@dataclass(frozen=True, slots=True)
class ProjectedEvent:
    event_type: PublicEventType
    data: dict[str, Any]


class StreamEventProjector:
    def __init__(self, *, public_nodes: frozenset[str] = frozenset({"model"})) -> None:
        self._public_nodes = public_nodes

    _CUSTOM_TYPES = {
        PublicEventType.TOOL_STARTED.value: PublicEventType.TOOL_STARTED,
        PublicEventType.TOOL_COMPLETED.value: PublicEventType.TOOL_COMPLETED,
    }

    def project(self, raw_event: Any) -> tuple[ProjectedEvent, ...]:
        # v2 namespaces must be explicit: missing provenance is not public.
        if self._field(raw_event, "ns") not in ((), []):
            return ()
        event_type = self._field(raw_event, "type")
        data = self._field(raw_event, "data")
        if event_type == "messages":
            return self._project_message(data)
        if event_type == "custom":
            return self._project_custom(data)
        return ()

    @staticmethod
    def _field(event: Any, name: str) -> Any:
        if isinstance(event, dict):
            return event.get(name)
        return getattr(event, name, None)

    def _project_message(self, data: Any) -> tuple[ProjectedEvent, ...]:
        if not isinstance(data, (tuple, list)) or len(data) != 2:
            return ()
        message, metadata = data
        if (
            not isinstance(metadata, dict)
            or metadata.get("langgraph_node") not in self._public_nodes
        ):
            return ()
        tags = metadata.get("tags", ())
        if not isinstance(tags, (tuple, list)) or any(
            tag in ("nostream", "private") for tag in tags
        ):
            return ()
        if not isinstance(message, AIMessageChunk):
            return ()
        text = message.content
        if isinstance(text, list):
            text = "".join(
                block if isinstance(block, str) else block["text"]
                for block in text
                if isinstance(block, str) or (
                    isinstance(block, dict) and block.get("type") == "text"
                    and isinstance(block.get("text"), str)
                )
            )
        if not isinstance(text, str) or not text:
            return ()
        return (ProjectedEvent(PublicEventType.MESSAGE_DELTA, {"text": text}),)

    def _project_custom(self, data: Any) -> tuple[ProjectedEvent, ...]:
        if not isinstance(data, dict) or data.get("public") is not True:
            return ()
        public_type = self._CUSTOM_TYPES.get(data.get("event"))
        public_data = data.get("data")
        if public_type is None or not isinstance(public_data, dict):
            return ()
        return (ProjectedEvent(public_type, public_data),)
