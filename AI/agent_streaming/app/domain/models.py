from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Transport(StrEnum):
    STREAMING_RESPONSE = "streaming_response"
    EVENT_SOURCE_RESPONSE = "event_source_response"


class RunStatus(StrEnum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatRun(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    thread_id: str
    transport: Transport
    status: RunStatus
    started_at: datetime
    model: str


class ChatMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID
    run_id: UUID
    thread_id: str
    role: MessageRole
    content: str
    created_at: datetime
