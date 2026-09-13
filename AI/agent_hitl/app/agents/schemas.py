from typing import NotRequired

from deepagents.graph import DeepAgentState
from pydantic import BaseModel

from app.domain.models import Segment, ValidationSegment


class AnalysisResult(BaseModel):
    format: str = "txt"
    encoding: str = "utf-8"
    paragraph_count: int


class ExtractionResult(BaseModel):
    segments: list[Segment]


class TranslationResult(BaseModel):
    segments: list[dict]


class ValidationAgentResult(BaseModel):
    result_type: str = "translation_validation_completed"
    validation_run_id: str
    revision: int = 1
    segments: list[ValidationSegment]


class FileTranslationState(DeepAgentState):
    run_id: NotRequired[str]
    review_status: NotRequired[str]
    reviewed_validation_run_id: NotRequired[str]
    review_request: NotRequired[dict]
    final_translations: NotRequired[list[dict]]
    phase: NotRequired[str]
    source_segments: NotRequired[list[dict]]
    input_hash: NotRequired[str]
    initial_translations: NotRequired[dict[str, str]]
    current_translations: NotRequired[dict[str, str]]
    current_revision: NotRequired[int]
    validation: NotRequired[dict]
    review_round: NotRequired[int]
    pending_command: NotRequired[dict | None]
    active_task: NotRequired[dict | None]
    task_results: NotRequired[dict]
    review_history: NotRequired[list[dict]]
    applied_commands: NotRequired[list[str]]
    approved_revision: NotRequired[int | None]
    approved_content_hash: NotRequired[str | None]
    revision_scope: NotRequired[list[str]]
    revision_instruction: NotRequired[str]
    output_path: NotRequired[str]
    retry_task: NotRequired[dict | None]
