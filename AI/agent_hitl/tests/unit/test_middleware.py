import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agents.middleware import (
    DocumentDelegationMiddleware,
    FilePipelineMiddleware,
    completed_subagents,
    extract_run_id,
    extract_txt_content,
    find_validation_result,
)


def test_finds_validation_result_for_matching_subagent_task():
    payload = {
        "result_type": "translation_validation_completed",
        "validation_run_id": "validation:run-1:1",
        "revision": 1,
        "segments": [
            {
                "segment_id": "segment-0001",
                "original_text": "Hello",
                "first_translation": "안녕",
                "validated_translation": "안녕하세요",
                "validation_note": "존댓말",
            }
        ],
    }
    messages = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "task",
                    "args": {"subagent_type": "file-validation", "description": "검증"},
                    "id": "call-1",
                }
            ],
        ),
        ToolMessage(content=json.dumps(payload, ensure_ascii=False), tool_call_id="call-1"),
    ]

    result = find_validation_result(messages)

    assert result is not None
    assert result.validation_run_id == "validation:run-1:1"


def test_ignores_same_payload_from_another_subagent():
    messages = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "task",
                    "args": {"subagent_type": "file-translator"},
                    "id": "call-2",
                }
            ],
        ),
        ToolMessage(
            content='{"result_type":"translation_validation_completed"}',
            tool_call_id="call-2",
        ),
    ]
    assert find_validation_result(messages) is None


def test_ignores_invalid_json():
    messages = [ToolMessage(content="not-json", tool_call_id="call-3")]
    assert find_validation_result(messages) is None


def test_extract_run_id_uses_original_task_message():
    messages = [HumanMessage(content="run_id=actual-run-id\nTXT를 번역하세요")]
    assert extract_run_id(messages) == "actual-run-id"


def test_extract_txt_content_excludes_runtime_metadata_and_instruction():
    messages = [
        HumanMessage(content="run_id=r1\nTranslate this TXT.\n\nHello world.\nHow are you?")
    ]
    assert extract_txt_content(messages) == "Hello world.\nHow are you?"


def test_completed_subagents_correlates_task_calls_and_results():
    messages = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "task",
                    "args": {"subagent_type": "file-translation"},
                    "id": "task-1",
                }
            ],
        ),
        ToolMessage(content="done", tool_call_id="task-1"),
    ]
    assert completed_subagents(messages) == {"file-translation"}


def test_document_middleware_schedules_file_translation_without_model_choice():
    result = DocumentDelegationMiddleware().before_model(
        {"messages": [HumanMessage(content="translate")]}, None
    )
    assert result["jump_to"] == "tools"
    assert result["messages"][0].tool_calls[0]["args"]["subagent_type"] == "file-translation"


def test_file_pipeline_schedules_first_missing_stage():
    result = FilePipelineMiddleware().before_model(
        {"messages": [HumanMessage(content="run_id=r1\ntranslate")]}, None
    )
    assert result["jump_to"] == "tools"
    assert result["messages"][0].tool_calls[0]["args"]["subagent_type"] == "file-analyzer"
