import json
from uuid import uuid4

from langchain.agents.middleware import AgentMiddleware, hook_config
from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from app.agents.schemas import FileTranslationState
from app.domain.models import ReviewDecision, ReviewRequest
from app.domain.review import resolve_review
from app.domain.revisions import apply_edits, content_hash, validate_action
from app.storage.files import parse_txt


def schedule(state, role, payload, **updates):
    task_id = f"task-{uuid4()}"
    active = {
        "id": task_id,
        "role": role,
        "revision": updates.get("current_revision", state.get("current_revision", 1)),
        "revising": role == "file-translator" and state.get("phase") == "REVISING",
        "payload": payload,
    }
    call = {
        "name": "task",
        "args": {"subagent_type": role, "description": json.dumps(payload, ensure_ascii=False)},
        "id": task_id,
    }
    if role == "replace_file":
        call = {"name": "replace_file", "args": {}, "id": task_id}
    return {
        **updates,
        "active_task": active,
        "messages": [AIMessage(content="", tool_calls=[call])],
        "jump_to": "tools",
    }


class TranslationReviewGateMiddleware(AgentMiddleware):
    state_schema = FileTranslationState

    def before_model(self, state, runtime):
        if state.get("phase") != "WAITING_REVIEW":
            return None
        raw = interrupt(state["review_request"])
        action = validate_action(ReviewRequest.model_validate(state["review_request"]), raw)
        return {"pending_command": action.model_dump(), "phase": "INTERPRETING"}


class FilePipelineMiddleware(AgentMiddleware):
    state_schema = FileTranslationState

    @hook_config(can_jump_to=["tools", "end"])
    def before_model(self, state, runtime):
        from app.agents.middleware import extract_run_id, extract_txt_content

        phase = state.get("phase")
        if phase is None:
            original = extract_txt_content(state["messages"])
            segments = [s.model_dump() for s in parse_txt(original.encode()).segments]
            return schedule(
                state,
                "file-analyzer",
                {"text": original},
                phase="ANALYZING",
                run_id=extract_run_id(state["messages"]),
                source_segments=segments,
                input_hash=content_hash(original),
                current_revision=1,
            )
        if phase == "EXTRACTING":
            return schedule(state, "file-extractor", {"segments": state["source_segments"]})
        if phase in {"TRANSLATING", "REVISING"}:
            return schedule(
                state,
                "file-translator",
                {
                    "source_segments": state["source_segments"],
                    "current_translations": state.get("current_translations", {}),
                    "target_ids": state.get(
                        "revision_scope", [s["segment_id"] for s in state["source_segments"]]
                    ),
                    "instruction": state.get("revision_instruction", "한국어로 번역하세요."),
                },
            )
        if phase == "VALIDATING":
            return schedule(
                state,
                "file-validation",
                {
                    "source_segments": state["source_segments"],
                    "translations": state["current_translations"],
                    "revision": state["current_revision"],
                },
            )
        if phase == "INTERPRETING":
            return self.route_command(state)
        if phase == "RETRYING":
            task = state["retry_task"]
            resumed = {**state, "phase": "REVISING" if task.get("revising") else "RETRYING"}
            return schedule(resumed, task["role"], task["payload"], retry_task=None)
        if phase == "COMPLETED":
            return {"messages": [AIMessage(content=state["output_path"])], "jump_to": "end"}
        raise ValueError(f"예상하지 못한 실행 상태: {phase}")

    def route_command(self, state):
        action = state["pending_command"]
        applied = state.get("applied_commands", [])
        if action["command_id"] in applied:
            raise ValueError("이미 처리된 명령입니다.")
        updates = {"pending_command": None, "applied_commands": [*applied, action["command_id"]]}
        if action["action"] == "message":
            history = [
                *state.get("review_history", []),
                {"role": "user", "content": action["message"]},
            ]
            return schedule(
                state,
                "review-conversation",
                {
                    "review": state["review_request"],
                    "history": history,
                    "message": action["message"],
                },
                **updates,
                review_history=history,
                phase="EXPLAINING",
            )
        if action["action"] == "edit":
            current = apply_edits(state["current_translations"], action["edits"])
            revision = state["current_revision"] + 1
            return schedule(
                state,
                "file-validation",
                {
                    "source_segments": state["source_segments"],
                    "translations": current,
                    "revision": revision,
                },
                **updates,
                current_translations=current,
                current_revision=revision,
                approved_revision=None,
                approved_content_hash=None,
                phase="VALIDATING",
                review_history=[
                    *state.get("review_history", []),
                    {"role": "user", "content": "직접 편집을 적용했습니다."},
                ],
            )
        final = resolve_review(
            ReviewRequest.model_validate(state["review_request"]),
            ReviewDecision(
                review_request_id=action["review_request_id"],
                revision=action["revision"],
                decisions=action["decisions"],
            ),
        )
        payload = [s.model_dump() for s in final]
        return schedule(
            state,
            "replace_file",
            {},
            **updates,
            phase="FINALIZING",
            final_translations=payload,
            approved_revision=state["current_revision"],
            approved_content_hash=content_hash(payload),
            review_status="completed",
        )
