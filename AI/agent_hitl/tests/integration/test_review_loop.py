import json
import os
from collections import Counter
from uuid import uuid4

import pytest
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agents.document import create_document_agent
from app.storage.files import LocalRunFileStore


class FixedModel(BaseChatModel):
    reply: str = "done"

    @property
    def _llm_type(self):
        return "test-fixed"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=self.reply))])


def specs():
    from langchain.agents.middleware import AgentMiddleware

    counts = Counter()

    class Count(AgentMiddleware):
        def __init__(self, role):
            self.role = role

        def before_model(self, state, runtime):
            counts[self.role] += 1

    replies = {
        "file-analyzer": {"format": "txt", "encoding": "utf-8", "paragraph_count": 1},
        "file-extractor": {
            "segments": [{"segment_id": "segment-0001", "order": 0, "original_text": "Hello"}]
        },
        "file-translator": {
            "segments": [{"segment_id": "segment-0001", "translated_text": "안녕"}]
        },
        "file-validation": {
            "segments": [
                {
                    "segment_id": "segment-0001",
                    "validated_translation": "안녕하세요",
                    "validation_note": "존댓말",
                }
            ]
        },
        "review-conversation": {
            "intent": "explain",
            "message": "존댓말 표현입니다.",
            "scope": "all",
            "segment_ids": [],
            "instruction": "",
        },
    }
    return [
        dict(
            name=role,
            description=role,
            runnable=create_agent(
                FixedModel(reply=json.dumps(reply, ensure_ascii=False)), middleware=[Count(role)]
            ),
        )
        for role, reply in replies.items()
    ], counts


async def exercise(tmp_path, checkpointer):
    files = LocalRunFileStore(tmp_path)
    run_id = str(uuid4())
    files.save_input(run_id, b"Hello")
    subagents, counts = specs()

    def build():
        return create_document_agent(FixedModel(), files, checkpointer, subagent_specs=subagents)

    config = {"configurable": {"thread_id": run_id}, "recursion_limit": 150}
    result = await build().ainvoke(
        {"messages": [{"role": "user", "content": f"run_id={run_id}\nTranslate\n\nHello"}]},
        config,
        version="v2",
    )
    request = result.interrupts[0].value
    assert request["revision"] == 1
    for i in range(2):
        result = await build().ainvoke(
            Command(
                resume={
                    result.interrupts[0].id: {
                        "command_id": f"explain-{i}",
                        "action": "message",
                        "message": "왜?",
                        "revision": request["revision"],
                        "review_request_id": request["review_request_id"],
                        "snapshot_hash": request["snapshot_hash"],
                    }
                }
            ),
            config,
            version="v2",
        )
        previous = request
        request = result.interrupts[0].value
        assert request["revision"] == 1
        assert request["review_request_id"] != previous["review_request_id"]
    assert counts["file-translator"] == counts["file-validation"] == 1
    result = await build().ainvoke(
        Command(
            resume={
                result.interrupts[0].id: {
                    "command_id": "edit",
                    "action": "edit",
                    "edits": {"segment-0001": "こんにちは"},
                    "revision": 1,
                    "review_request_id": request["review_request_id"],
                    "snapshot_hash": request["snapshot_hash"],
                }
            }
        ),
        config,
        version="v2",
    )
    request = result.interrupts[0].value
    assert request["revision"] == 2
    assert request["segments"][0]["first_translation"] == "こんにちは"
    assert counts["file-analyzer"] == counts["file-extractor"] == 1
    assert counts["file-validation"] == 2
    assert not (tmp_path / run_id / "output.txt").exists()
    result = await build().ainvoke(
        Command(
            resume={
                result.interrupts[0].id: {
                    "command_id": "approve",
                    "action": "approve",
                    "revision": 2,
                    "review_request_id": request["review_request_id"],
                    "snapshot_hash": request["snapshot_hash"],
                    "decisions": [{"segment_id": "segment-0001", "selected": "first"}],
                }
            }
        ),
        config,
        version="v2",
    )
    assert not result.interrupts
    assert (tmp_path / run_id / "output.txt").read_text(encoding="utf-8") == "こんにちは"


@pytest.mark.asyncio
async def test_nested_review_loop(tmp_path):
    await exercise(tmp_path, InMemorySaver())


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("RUN_REDIS_TESTS") != "1", reason="RUN_REDIS_TESTS=1 required")
async def test_nested_review_loop_redis(tmp_path):
    from langgraph.checkpoint.redis.aio import AsyncRedisSaver

    async with AsyncRedisSaver.from_conn_string("redis://localhost:6379") as saver:
        await saver.asetup()
        await exercise(tmp_path, saver)


@pytest.mark.parametrize("intent,revision,translation_calls", [("revise", 2, 2), ("clarify", 1, 1)])
@pytest.mark.asyncio
async def test_conversation_routes_without_repeating_initial_work(
    tmp_path, intent, revision, translation_calls
):
    subagents, counts = specs()
    for sub in subagents:
        if sub["name"] == "review-conversation":
            sub["runnable"] = create_agent(
                FixedModel(
                    reply=json.dumps(
                        {
                            "intent": intent,
                            "message": "응답",
                            "scope": "all",
                            "segment_ids": [],
                            "instruction": "존댓말로 수정",
                        }
                    )
                )
            )
    run_id = str(uuid4())
    files = LocalRunFileStore(tmp_path)
    files.save_input(run_id, b"Hello")
    agent = create_document_agent(FixedModel(), files, InMemorySaver(), subagent_specs=subagents)
    config = {"configurable": {"thread_id": run_id}, "recursion_limit": 150}
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": f"run_id={run_id}\nTranslate\n\nHello"}]},
        config,
        version="v2",
    )
    request = result.interrupts[0].value
    result = await agent.ainvoke(
        Command(
            resume={
                result.interrupts[0].id: {
                    "command_id": "chat",
                    "action": "message",
                    "message": "바꿔줘",
                    "revision": 1,
                    "review_request_id": request["review_request_id"],
                    "snapshot_hash": request["snapshot_hash"],
                }
            }
        ),
        config,
        version="v2",
    )
    assert result.interrupts[0].value["revision"] == revision
    assert counts["file-translator"] == counts["file-validation"] == translation_calls
    assert counts["file-analyzer"] == counts["file-extractor"] == 1
    assert not (tmp_path / run_id / "output.txt").exists()
