from deepagents import create_deep_agent
from langchain_core.language_models import BaseChatModel

from app.agents.middleware import FilePipelineMiddleware, TranslationReviewGateMiddleware
from app.agents.schemas import (
    AnalysisResult,
    ExtractionResult,
    FileTranslationState,
    TranslationResult,
    ValidationAgentResult,
)
from app.agents.tools import create_replace_tool
from app.storage.files import LocalRunFileStore


def create_file_translation_agent(model: BaseChatModel, file_store: LocalRunFileStore):
    subagents = [
        {
            "name": "file-analyzer",
            "description": "TXT 파일의 형식, 인코딩, 문단 수를 분석합니다.",
            "system_prompt": "입력된 TXT 정보만 분석하고 구조화된 결과를 반환하세요.",
            "response_format": AnalysisResult,
        },
        {
            "name": "file-extractor",
            "description": "TXT의 비어 있지 않은 각 줄을 순서가 있는 segment로 추출합니다.",
            "system_prompt": (
                "각 비어 있지 않은 줄을 segment로 추출하세요. "
                "ID는 segment-0001부터 순서대로 생성하세요."
            ),
            "response_format": ExtractionResult,
        },
        {
            "name": "file-translator",
            "description": "추출된 각 segment를 한국어로 1차 번역합니다.",
            "system_prompt": (
                "각 segment를 자연스러운 한국어로 번역하세요. "
                "segment_id, original_text, translated_text를 보존하세요."
            ),
            "response_format": TranslationResult,
        },
        {
            "name": "file-validation",
            "description": "1차 번역을 검증하고 원문, 초안, 검증본, 수정 사유를 반환합니다.",
            "system_prompt": (
                "run_id와 1차 번역을 검증하세요. result_type은 반드시 "
                "translation_validation_completed, validation_run_id는 "
                "validation:{run_id}:1로 반환하세요. 각 segment에 원문, 1차 번역, "
                "검증 번역, 검증 사유를 포함하세요."
            ),
            "response_format": ValidationAgentResult,
        },
    ]
    return create_deep_agent(
        model=model,
        tools=[create_replace_tool(file_store)],
        subagents=subagents,
        middleware=[FilePipelineMiddleware(), TranslationReviewGateMiddleware()],
        state_schema=FileTranslationState,
        system_prompt=(
            "당신은 File Translation Agent입니다. run_id와 TXT 내용을 받습니다. "
            "file-analyzer, file-extractor, file-translator, file-validation을 반드시 "
            "이 순서로 한 번씩 호출하세요. 각 다음 task description에 앞선 구조화 결과와 "
            "run_id를 포함하세요. Validation 후 시스템이 사람 검수를 중단시킵니다. "
            "검수 완료 안내를 받으면 인자 없이 replace_file 도구를 호출하고 결과 경로를 반환하세요."
        ),
    )
