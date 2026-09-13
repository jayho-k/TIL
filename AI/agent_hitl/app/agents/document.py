from deepagents import create_deep_agent
from deepagents.middleware.subagents import CompiledSubAgent
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver

from app.agents.middleware import DocumentDelegationMiddleware
from app.agents.subagents import create_file_translation_agent
from app.storage.files import LocalRunFileStore


def create_document_agent(
    model: BaseChatModel,
    file_store: LocalRunFileStore,
    checkpointer: BaseCheckpointSaver,
    *,
    subagent_specs=None,
):
    file_agent = create_file_translation_agent(model, file_store, subagent_specs=subagent_specs)
    file_subagent: CompiledSubAgent = {
        "name": "file-translation",
        "description": "TXT 파일을 분석, 추출, 번역, 검증, 사람 검수 후 교체합니다.",
        "runnable": file_agent,
    }
    document = create_deep_agent(
        model=model,
        subagents=[file_subagent],
        middleware=[DocumentDelegationMiddleware()],
        checkpointer=checkpointer,
        system_prompt=(
            "당신은 Document Agent입니다. TXT 번역 요청은 file-translation SubAgent에 "
            "정확히 한 번 위임하고 그 결과를 반환하세요."
        ),
    )
    document.file_translation_graph = file_agent
    return document
