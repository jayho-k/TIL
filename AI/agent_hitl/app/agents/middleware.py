import json
import re
from typing import Any
from uuid import uuid4

from langchain.agents.middleware import AgentMiddleware, hook_config
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.types import interrupt

from app.agents.schemas import FileTranslationState
from app.domain.models import ReviewDecision, ReviewRequest, ValidationResult
from app.domain.review import resolve_review

_RUN_ID_PATTERN = re.compile(r"(?:^|\n)run_id=([^\s]+)")


def extract_run_id(messages: list[BaseMessage]) -> str | None:
    for message in messages:
        if isinstance(message, HumanMessage) and isinstance(message.content, str):
            match = _RUN_ID_PATTERN.search(message.content)
            if match:
                return match.group(1)
    return None


def extract_txt_content(messages: list[BaseMessage]) -> str:
    for message in messages:
        if not isinstance(message, HumanMessage) or not isinstance(message.content, str):
            continue
        _, separator, content = message.content.partition("\n\n")
        return content if separator else message.content
    return ""


def _task_targets(messages: list[BaseMessage]) -> dict[str, str]:
    targets: dict[str, str] = {}
    for message in messages:
        if not isinstance(message, AIMessage):
            continue
        for call in message.tool_calls:
            if call.get("name") == "task":
                args = call.get("args", {})
                target = args.get("subagent_type") or args.get("name")
                if target:
                    targets[call["id"]] = target
    return targets


def find_validation_result(messages: list[BaseMessage]) -> ValidationResult | None:
    targets = _task_targets(messages)
    for message in reversed(messages):
        if not isinstance(message, ToolMessage):
            continue
        if targets.get(message.tool_call_id) != "file-validation":
            continue
        if not isinstance(message.content, str):
            continue
        try:
            return ValidationResult.model_validate(json.loads(message.content))
        except (json.JSONDecodeError, ValueError):
            continue
    return None


def completed_subagents(messages: list[BaseMessage]) -> set[str]:
    targets = _task_targets(messages)
    return {
        targets[message.tool_call_id]
        for message in messages
        if isinstance(message, ToolMessage) and message.tool_call_id in targets
    }


def latest_subagent_result(messages: list[BaseMessage], subagent_type: str) -> str | None:
    targets = _task_targets(messages)
    for message in reversed(messages):
        if isinstance(message, ToolMessage) and targets.get(message.tool_call_id) == subagent_type:
            return str(message.content)
    return None


def _task_call(subagent_type: str, description: str) -> dict[str, Any]:
    return {
        "messages": [AIMessage(content="", tool_calls=[{
            "name": "task",
            "args": {"subagent_type": subagent_type, "description": description},
            "id": f"task-{uuid4()}",
        }])],
        "jump_to": "tools",
    }


class DocumentDelegationMiddleware(AgentMiddleware):
    @hook_config(can_jump_to=["tools"])
    def before_model(self, state: dict[str, Any], runtime: Any) -> dict[str, Any] | None:
        messages = state["messages"]
        if "file-translation" in completed_subagents(messages):
            return None
        request = next(
            (str(message.content) for message in messages if isinstance(message, HumanMessage)),
            "TXT 파일을 번역하세요.",
        )
        return _task_call("file-translation", request)


class FilePipelineMiddleware(AgentMiddleware):
    stages = ("file-analyzer", "file-extractor", "file-translator", "file-validation")

    @hook_config(can_jump_to=["tools"])
    def before_model(self, state: FileTranslationState, runtime: Any) -> dict[str, Any] | None:
        messages = state["messages"]
        done = completed_subagents(messages)
        original = extract_txt_content(messages)
        descriptions = {
            "file-analyzer": f"다음 TXT 파일의 구조를 분석하세요.\n\n{original}",
            "file-extractor": (
                "다음 원문에서 번역할 텍스트를 순서대로 추출하세요.\n\n"
                f"원문:\n{original}\n\n분석 결과:\n"
                f"{latest_subagent_result(messages, 'file-analyzer')}"
            ),
            "file-translator": (
                "다음 추출 결과의 각 segment를 한국어로 번역하세요.\n\n"
                f"{latest_subagent_result(messages, 'file-extractor')}"
            ),
            "file-validation": (
                f"run_id={extract_run_id(messages)}\n"
                "다음 1차 번역을 검증하고 구조화된 검증 결과를 반환하세요.\n\n"
                f"{latest_subagent_result(messages, 'file-translator')}"
            ),
        }
        for stage in self.stages:
            if stage not in done:
                return _task_call(stage, descriptions[stage])

        # 검증 직후에는 다음 middleware가 interrupt를 수행해야 한다.
        if state.get("review_status") != "completed":
            return None
        if any(
            isinstance(message, ToolMessage) and message.name == "replace_file"
            for message in messages
        ):
            return None
        return {
            "messages": [AIMessage(content="", tool_calls=[{
                "name": "replace_file", "args": {}, "id": f"replace-{uuid4()}"
            }])],
            "jump_to": "tools",
        }


class TranslationReviewGateMiddleware(AgentMiddleware):
    state_schema = FileTranslationState

    def before_model(self, state: FileTranslationState, runtime: Any) -> dict[str, Any] | None:
        run_id = state.get("run_id") or extract_run_id(state["messages"])
        if not run_id:
            return None
        validation = find_validation_result(state["messages"])
        if validation is None:
            return {"run_id": run_id} if "run_id" not in state else None
        stable_validation_id = f"validation:{run_id}:{validation.revision}"
        if state.get("reviewed_validation_run_id") == stable_validation_id:
            return None

        request = ReviewRequest(
            review_request_id=f"review:{stable_validation_id}",
            revision=validation.revision,
            segments=validation.segments,
        )
        raw_decision = interrupt(request.model_dump(mode="json"))
        decision = ReviewDecision.model_validate(raw_decision)
        final = resolve_review(request, decision)
        return {
            "review_status": "completed",
            "run_id": run_id,
            "reviewed_validation_run_id": stable_validation_id,
            "review_request": request.model_dump(mode="json"),
            "final_translations": [item.model_dump(mode="json") for item in final],
            "messages": [HumanMessage(content="사람의 번역 검수가 완료되었습니다.")],
        }
