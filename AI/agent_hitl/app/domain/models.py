from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Segment(BaseModel):
    segment_id: str
    order: int
    original_text: str


class ValidationSegment(BaseModel):
    segment_id: str
    original_text: str
    first_translation: str
    validated_translation: str
    validation_note: str


class ValidationResult(BaseModel):
    result_type: Literal["translation_validation_completed"] = "translation_validation_completed"
    validation_run_id: str
    revision: int = 1
    segments: list[ValidationSegment]


class ReviewRequest(BaseModel):
    type: Literal["translation_review_required"] = "translation_review_required"
    review_request_id: str
    revision: int
    segments: list[ValidationSegment]
    snapshot_hash: str = ""
    history: list[dict] = Field(default_factory=list)
    initial_translations: dict[str, str] = Field(default_factory=dict)


class SegmentDecision(BaseModel):
    segment_id: str
    selected: Literal["first", "validated", "custom"]
    custom_text: str | None = None


class ReviewDecision(BaseModel):
    review_request_id: str
    revision: int
    decisions: list[SegmentDecision]


class FinalTranslation(BaseModel):
    segment_id: str
    translated_text: str


class RunStatus(StrEnum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"
    RESUMING = "RESUMING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


class RunRecord(BaseModel):
    run_id: str
    thread_id: str
    status: RunStatus = RunStatus.CREATED
    input_path: str
    output_path: str | None = None
    review_request: ReviewRequest | None = None
    decision_hash: str | None = None
    validation_call_count: int = Field(default=0, ge=0)
    replace_call_count: int = Field(default=0, ge=0)
    interrupt_id: str | None = None
    active_command: dict | None = None
    commands: dict[str, dict] = Field(default_factory=dict)
    history: list[dict] = Field(default_factory=list)
    error: str | None = None
