import json
import re
from typing import Any
from uuid import uuid4

from langchain.agents.middleware import AgentMiddleware, hook_config
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage

from app.domain.models import ValidationResult

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
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "task",
                        "args": {"subagent_type": subagent_type, "description": description},
                        "id": f"task-{uuid4()}",
                    }
                ],
            )
        ],
        "jump_to": "tools",
    }


class DocumentDelegationMiddleware(AgentMiddleware):
    @hook_config(can_jump_to=["tools", "end"])
    def before_model(self, state: dict[str, Any], runtime: Any) -> dict[str, Any] | None:
        messages = state["messages"]
        targets = _task_targets(messages)
        for message in reversed(messages):
            if (
                isinstance(message, ToolMessage)
                and targets.get(message.tool_call_id) == "file-translation"
            ):
                if message.status == "error":
                    raise ValueError("File Translation 작업이 실패했습니다.")
                return {"messages": [AIMessage(content=str(message.content))], "jump_to": "end"}
        if "file-translation" in completed_subagents(messages):
            return None
        request = next(
            (str(message.content) for message in messages if isinstance(message, HumanMessage)),
            "TXT 파일을 번역하세요.",
        )
        return _task_call("file-translation", request)


from app.agents.pipeline import (  # noqa: E402,F401
    FilePipelineMiddleware,
    TranslationReviewGateMiddleware,
)
