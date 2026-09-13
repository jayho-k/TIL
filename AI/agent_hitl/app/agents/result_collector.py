import json

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage

from app.agents.review_conversation import ConversationResult
from app.agents.schemas import AnalysisResult, ExtractionResult, FileTranslationState
from app.domain.models import ReviewRequest, ValidationSegment
from app.domain.revisions import apply_edits, content_hash


def open_review(state, **updates):
    merged = {**state, **updates}
    round_number = merged.get("review_round", 0) + 1
    validation = merged["validation"]
    request = ReviewRequest(
        review_request_id=f"review:{merged['run_id']}:{merged['current_revision']}:{round_number}",
        revision=merged["current_revision"],
        segments=validation["segments"],
        history=merged.get("review_history", []),
        initial_translations=merged.get("initial_translations", {}),
        snapshot_hash=content_hash(
            {
                "input": merged["input_hash"],
                "revision": merged["current_revision"],
                "segments": validation["segments"],
            }
        ),
    )
    return {
        **updates,
        "phase": "WAITING_REVIEW",
        "review_round": round_number,
        "review_request": request.model_dump(mode="json"),
        "review_status": "pending",
    }


def indexed_segments(raw, expected):
    segments = raw["segments"]
    indexed = {s["segment_id"]: s for s in segments}
    if len(indexed) != len(segments) or set(indexed) != set(expected):
        raise ValueError("Agent 결과 segment ID 누락, 중복 또는 범위 불일치")
    return indexed


class ResultCollectorMiddleware(AgentMiddleware):
    state_schema = FileTranslationState

    def before_model(self, state, runtime):
        active = state.get("active_task")
        if not active:
            return None
        result = next(
            (
                m
                for m in reversed(state["messages"])
                if isinstance(m, ToolMessage) and m.tool_call_id == active["id"]
            ),
            None,
        )
        if result is None or result.status == "error":
            raise ValueError("작업 성공 결과가 없습니다.")
        if active["revision"] != state["current_revision"]:
            raise ValueError("현재 revision과 작업 결과가 일치하지 않습니다.")
        raw = json.loads(result.content)
        role = active["role"]
        updates = {
            "active_task": None,
            "task_results": {
                **state.get("task_results", {}),
                active["id"]: {**active, "success": True},
            },
        }
        if role == "file-analyzer":
            AnalysisResult.model_validate(raw)
            updates["phase"] = "EXTRACTING"
        elif role == "file-extractor":
            extracted = ExtractionResult.model_validate(raw)
            if [s.model_dump() for s in extracted.segments] != state["source_segments"]:
                raise ValueError("추출 결과가 서버 원문과 다릅니다.")
            updates["phase"] = "TRANSLATING"
        elif role == "file-translator":
            revising = active.get("revising", False)
            expected = (
                state["revision_scope"]
                if revising
                else [s["segment_id"] for s in state["source_segments"]]
            )
            indexed = indexed_segments(raw, expected)
            translated = {key: value["translated_text"] for key, value in indexed.items()}
            if any(not isinstance(t, str) or not t.strip() for t in translated.values()):
                raise ValueError("번역문이 비어 있습니다.")
            if revising:
                updates.update(
                    current_translations=apply_edits(state["current_translations"], translated),
                    current_revision=state["current_revision"] + 1,
                    approved_revision=None,
                    approved_content_hash=None,
                )
            else:
                updates.update(current_translations=translated, initial_translations=translated)
            updates["phase"] = "VALIDATING"
        elif role == "file-validation":
            indexed = indexed_segments(raw, state["current_translations"])
            segments = []
            for source in state["source_segments"]:
                key = source["segment_id"]
                candidate = indexed[key]
                if not candidate["validated_translation"].strip():
                    raise ValueError("검증 번역문이 비어 있습니다.")
                segments.append(
                    ValidationSegment(
                        segment_id=key,
                        original_text=source["original_text"],
                        first_translation=state["current_translations"][key],
                        validated_translation=candidate["validated_translation"],
                        validation_note=candidate["validation_note"],
                    ).model_dump()
                )
            updates["validation"] = {
                "revision": state["current_revision"],
                "input_hash": content_hash(state["current_translations"]),
                "segments": segments,
            }
            return open_review(state, **updates)
        elif role == "review-conversation":
            conversation = ConversationResult.model_validate(raw)
            history = [
                *state.get("review_history", []),
                {"role": "assistant", "content": conversation.message},
            ]
            updates["review_history"] = history
            if conversation.intent != "revise":
                return open_review(state, **updates)
            targets = (
                list(state["current_translations"])
                if conversation.scope == "all"
                else conversation.segment_ids
            )
            if (
                not targets
                or len(set(targets)) != len(targets)
                or not set(targets) <= set(state["current_translations"])
                or not conversation.instruction.strip()
            ):
                updates["review_history"] = [
                    *history,
                    {
                        "role": "assistant",
                        "content": "수정할 문단 번호와 원하는 변경을 구체적으로 알려주세요.",
                    },
                ]
                return open_review(state, **updates)
            updates.update(
                phase="REVISING",
                revision_scope=targets,
                revision_instruction=conversation.instruction,
            )
        elif role == "replace_file":
            updates.update(phase="COMPLETED", output_path=raw["output_path"])
        else:
            raise ValueError("알 수 없는 작업 결과입니다.")
        return updates
