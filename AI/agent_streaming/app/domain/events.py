from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PublicEventType(StrEnum):
    STREAM_STARTED = "stream.started"
    MESSAGE_DELTA = "message.delta"
    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    STREAM_COMPLETED = "stream.completed"
    STREAM_ERROR = "stream.error"


class StreamEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: str = "1"
    event_type: PublicEventType
    event_id: str
    run_id: UUID
    thread_id: str
    sequence: int = Field(ge=0)
    timestamp: datetime
    data: dict[str, Any]

    @classmethod
    def create(
        cls,
        *,
        event_type: PublicEventType,
        run_id: UUID,
        thread_id: str,
        sequence: int,
        data: dict[str, Any],
        timestamp: datetime | None = None,
    ) -> StreamEvent:
        return cls(
            event_type=event_type,
            event_id=f"{run_id}:{sequence}",
            run_id=run_id,
            thread_id=thread_id,
            sequence=sequence,
            timestamp=timestamp or datetime.now(UTC),
            data=data,
        )

    def payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json")
        payload.pop("event_type")
        return payload
