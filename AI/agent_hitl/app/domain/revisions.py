import hashlib
import json
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from app.domain.models import ReviewDecision, ReviewRequest, SegmentDecision
from app.domain.review import resolve_review


def content_hash(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


class ActionBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: str = Field(min_length=1, max_length=100)
    review_request_id: str
    revision: int = Field(ge=1)
    snapshot_hash: str


class MessageAction(ActionBase):
    action: Literal["message"]
    message: str = Field(min_length=1, max_length=10000)


class EditAction(ActionBase):
    action: Literal["edit"]
    edits: dict[str, str]


class ApproveAction(ActionBase):
    action: Literal["approve"]
    decisions: list[SegmentDecision]


ReviewAction = Annotated[MessageAction | EditAction | ApproveAction, Field(discriminator="action")]
action_adapter = TypeAdapter(ReviewAction)


def apply_edits(current: dict[str, str], edits: dict[str, str]) -> dict[str, str]:
    if not edits or not set(edits) <= set(current):
        raise ValueError("수정 대상 segment가 없거나 올바르지 않습니다.")
    if any(not text.strip() for text in edits.values()):
        raise ValueError("빈 번역문은 사용할 수 없습니다.")
    return {**current, **edits}


def validate_action(request: ReviewRequest, raw: dict):
    action = action_adapter.validate_python(raw)
    if (
        action.review_request_id != request.review_request_id
        or action.revision != request.revision
        or action.snapshot_hash != request.snapshot_hash
    ):
        raise ValueError("현재 검수 회차 또는 revision과 일치하지 않습니다.")
    if isinstance(action, MessageAction) and not action.message.strip():
        raise ValueError("메시지가 비어 있습니다.")
    if isinstance(action, EditAction):
        apply_edits({s.segment_id: s.first_translation for s in request.segments}, action.edits)
    if isinstance(action, ApproveAction):
        if any(d.selected == "custom" for d in action.decisions):
            raise ValueError("직접 편집은 수정 적용 후 재검증해야 합니다.")
        resolve_review(
            request,
            ReviewDecision(
                review_request_id=action.review_request_id,
                revision=action.revision,
                decisions=action.decisions,
            ),
        )
    return action
