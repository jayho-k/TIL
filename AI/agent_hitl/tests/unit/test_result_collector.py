import json

import pytest
from langchain_core.messages import ToolMessage

from app.agents.result_collector import ResultCollectorMiddleware


def state_for(role, payload, **updates):
    return {
        "messages": [ToolMessage(content=json.dumps(payload), tool_call_id="t1")],
        "active_task": {"id": "t1", "role": role, "revision": 2, "revising": True},
        "current_revision": 2,
        "current_translations": {"s1": "하나", "s2": "둘"},
        "revision_scope": ["s2"],
        "approved_revision": 1,
        "approved_content_hash": "old",
        **updates,
    }


def test_partial_revision_preserves_other_text_and_invalidates_approval():
    state = state_for(
        "file-translator", {"segments": [{"segment_id": "s2", "translated_text": "둘입니다"}]}
    )
    result = ResultCollectorMiddleware().before_model(state, None)
    assert result["current_translations"] == {"s1": "하나", "s2": "둘입니다"}
    assert result["current_revision"] == 3
    assert result["approved_revision"] is None
    assert result["approved_content_hash"] is None
    assert result["phase"] == "VALIDATING"


def test_outside_scope_and_error_result_do_not_advance():
    state = state_for(
        "file-translator", {"segments": [{"segment_id": "s1", "translated_text": "변경"}]}
    )
    with pytest.raises(ValueError):
        ResultCollectorMiddleware().before_model(state, None)
    state["messages"][0].status = "error"
    with pytest.raises(ValueError):
        ResultCollectorMiddleware().before_model(state, None)


def test_stale_result_rejected():
    state = state_for("file-translator", {}, current_revision=3)
    with pytest.raises(ValueError, match="revision"):
        ResultCollectorMiddleware().before_model(state, None)
