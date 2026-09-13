import json

from deepagents import create_deep_agent
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, hook_config
from langchain_core.messages import AIMessage
from pydantic import BaseModel

from app.agents.pipeline import FilePipelineMiddleware, TranslationReviewGateMiddleware
from app.agents.result_collector import ResultCollectorMiddleware
from app.agents.review_conversation import CONVERSATION_PROMPT, ConversationResult
from app.agents.schemas import AnalysisResult, FileTranslationState
from app.agents.tools import create_replace_tool


class TranslatedSegment(BaseModel):
    segment_id: str
    translated_text: str


class Translations(BaseModel):
    segments: list[TranslatedSegment]


class ValidatedSegment(BaseModel):
    segment_id: str
    validated_translation: str
    validation_note: str


class Validations(BaseModel):
    segments: list[ValidatedSegment]


class ExtractionMiddleware(AgentMiddleware):
    @hook_config(can_jump_to=["end"])
    def before_model(self, state, runtime):
        payload = json.loads(state["messages"][0].content)
        return {
            "messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))],
            "jump_to": "end",
        }


def create_file_translation_agent(model, file_store, *, subagent_specs=None):
    if subagent_specs is None:
        definitions = [
            ("file-analyzer", "TXT 구조를 분석하세요.", AnalysisResult),
            (
                "file-translator",
                "원문을 참고하여 target_ids에 지정된 항목만 instruction대로 "
                "번역/수정하세요. 지정된 ID를 빠짐없이 그대로 반환하세요. "
                "current_translations는 수정의 기준입니다.",
                Translations,
            ),
            (
                "file-validation",
                "원문과 translations를 비교해 각 ID의 검증본과 수정 사유를 "
                "한국어로 반환하세요. 모든 ID를 보존하세요.",
                Validations,
            ),
            ("review-conversation", CONVERSATION_PROMPT, ConversationResult),
        ]
        subagent_specs = [
            dict(
                name=name,
                description=prompt,
                runnable=create_agent(
                    model=model,
                    system_prompt=prompt,
                    response_format=schema,
                ),
            )
            for name, prompt, schema in definitions
        ]
        subagent_specs.append(
            dict(
                name="file-extractor",
                description="서버가 추출한 원문을 반환",
                runnable=create_agent(model=model, middleware=[ExtractionMiddleware()]),
            )
        )
    return create_deep_agent(
        model=model,
        tools=[create_replace_tool(file_store)],
        subagents=subagent_specs,
        middleware=[
            ResultCollectorMiddleware(),
            TranslationReviewGateMiddleware(),
            FilePipelineMiddleware(),
        ],
        state_schema=FileTranslationState,
        system_prompt="파일 번역 담당입니다. 시스템의 단계 및 검수 제어에 따릅니다.",
    )
