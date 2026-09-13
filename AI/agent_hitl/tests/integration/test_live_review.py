import os
from uuid import uuid4

import pytest
from langchain_core.callbacks import BaseCallbackHandler
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agents.document import create_document_agent
from app.agents.model import create_model
from app.config import Settings
from app.storage.files import LocalRunFileStore


@pytest.mark.live
@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="RUN_LIVE_TESTS=1 required")
@pytest.mark.asyncio
async def test_ollama_conversation_revision_approval(tmp_path):
    class Trace(BaseCallbackHandler):
        def on_chat_model_start(self, serialized, messages, **kwargs):
            print("model_call_started", flush=True)

        def on_llm_end(self, response, **kwargs):
            print("model_call_finished", flush=True)

    run_id = str(uuid4())
    files = LocalRunFileStore(tmp_path)
    source = "Hello, welcome to our service.\nPlease save your changes."
    files.save_input(run_id, source.encode())
    model = create_model(Settings()).model_copy(update={"request_timeout": 60, "max_retries": 0})
    agent = create_document_agent(model, files, InMemorySaver())
    config = {"configurable": {"thread_id": run_id}, "recursion_limit": 80, "callbacks": [Trace()]}
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": f"run_id={run_id}\nTranslate\n\n{source}"}]},
        config,
        version="v2",
    )
    assert result.interrupts
    print("initial_review_ok", flush=True)
    for message, revision in [
        ("첫 번째 문장을 왜 이렇게 번역했는지 설명만 해줘.", 1),
        ("모든 문장을 격식 있는 존댓말로 수정해줘.", 2),
    ]:
        request = result.interrupts[0].value
        result = await agent.ainvoke(
            Command(
                resume={
                    result.interrupts[0].id: {
                        "command_id": str(uuid4()),
                        "action": "message",
                        "message": message,
                        "review_request_id": request["review_request_id"],
                        "revision": request["revision"],
                        "snapshot_hash": request["snapshot_hash"],
                    }
                }
            ),
            config,
            version="v2",
        )
        assert result.interrupts
        assert result.interrupts[0].value["revision"] == revision
        print("review_revision", revision, flush=True)
    request = result.interrupts[0].value
    result = await agent.ainvoke(
        Command(
            resume={
                result.interrupts[0].id: {
                    "command_id": str(uuid4()),
                    "action": "approve",
                    "revision": request["revision"],
                    "review_request_id": request["review_request_id"],
                    "snapshot_hash": request["snapshot_hash"],
                    "decisions": [
                        {"segment_id": s["segment_id"], "selected": "validated"}
                        for s in request["segments"]
                    ],
                }
            }
        ),
        config,
        version="v2",
    )
    assert not result.interrupts
    assert (tmp_path / run_id / "output.txt").read_text(encoding="utf-8") == "\n".join(
        s["validated_translation"] for s in request["segments"]
    )
    print("approved_file_matches", flush=True)
