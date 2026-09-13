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
