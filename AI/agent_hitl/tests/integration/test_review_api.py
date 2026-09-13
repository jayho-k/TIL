import asyncio
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI
from langgraph.checkpoint.memory import InMemorySaver
from redis.exceptions import WatchError

from app.agents.document import create_document_agent
from app.api.routes import router
from app.domain.models import RunStatus
from app.runs.repository import RedisRunRepository, ReviewConflict
from app.service.runner import AgentRunner
from app.storage.files import LocalRunFileStore
from tests.integration.test_review_loop import FixedModel, specs


class MemoryRedis:
    def __init__(self):
        self.data = {}
        self.versions = {}

    async def get(self, key):
        await asyncio.sleep(0)
        return self.data.get(key)

    async def set(self, key, value):
        self.data[key] = value
        self.versions[key] = self.versions.get(key, 0) + 1

    def pipeline(self, **kwargs):
        owner = self

        class Pipeline:
            async def __aenter__(self):
                self.queued = []
                return self

            async def __aexit__(self, *args):
                return None

            async def watch(self, key):
                self.key, self.version = key, owner.versions.get(key, 0)

            async def get(self, key):
                return await owner.get(key)

            def multi(self):
                pass

            def set(self, key, value):
                self.queued.append((key, value))

            async def execute(self):
                if self.version != owner.versions.get(self.key, 0):
                    raise WatchError()
                for key, value in self.queued:
                    await owner.set(key, value)

        return Pipeline()


async def setup(tmp_path):
    files = LocalRunFileStore(tmp_path)
    subs, _ = specs()
    agent = create_document_agent(FixedModel(), files, InMemorySaver(), subagent_specs=subs)
    repo = RedisRunRepository(MemoryRedis())
    runner = AgentRunner(agent, repo, files)
    record = await runner.create_run(b"Hello")
    stream = await runner.launch_start(record.run_id, "Hello")
    async for _ in stream:
        pass
    record = await repo.get(record.run_id)
    assert record.status == RunStatus.WAITING_FOR_REVIEW
    request = record.review_request
    action = dict(
        command_id=str(uuid4()),
        action="message",
        message="왜?",
        revision=request.revision,
        review_request_id=request.review_request_id,
        snapshot_hash=request.snapshot_hash,
    )
    return runner, repo, record, action


@pytest.mark.asyncio
async def test_atomic_duplicate_and_new_round(tmp_path):
    runner, repo, record, action = await setup(tmp_path)
    results = await asyncio.gather(
        repo.accept_action(record.run_id, action), repo.accept_action(record.run_id, action)
    )
    assert sorted(results) == [False, True]
    other = {**action, "command_id": "another"}
    with pytest.raises(ReviewConflict):
        await repo.accept_action(record.run_id, other)
    await runner.close()


@pytest.mark.asyncio
async def test_invalid_request_does_not_consume_review_and_http_errors(tmp_path):
    runner, repo, record, action = await setup(tmp_path)
    app = FastAPI()
    app.include_router(router)
    app.state.runner, app.state.repository = runner, repo
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as c:
        url = f"/runs/{record.run_id}/review-actions"
        bad = {k: v for k, v in action.items() if k not in {"action", "message"}}
        response = await c.post(url, json={**bad, "action": "edit", "edits": {"bad": "text"}})
        assert response.status_code == 422
        response = await c.post(url, json={**action, "revision": 999})
        assert response.status_code == 409
        response = await c.post("/runs/missing/review-actions", json=action)
        assert response.status_code == 404
        response = await c.post(url, json=action)
        assert response.status_code == 200
        assert "hitl.required" in response.text
        updated = await repo.get(record.run_id)
        assert updated.review_request.review_request_id != action["review_request_id"]
        assert updated.review_request.revision == 1
    await runner.close()


@pytest.mark.asyncio
async def test_disconnect_does_not_cancel_work_and_recover_pending_accept(tmp_path):
    runner, repo, record, action = await setup(tmp_path)
    stream = await runner.submit_action(record.run_id, action)
    await stream.aclose()
    await runner.close()
    record = await repo.get(record.run_id)
    assert record.status == RunStatus.WAITING_FOR_REVIEW
    action = {
        **action,
        "command_id": "next",
        "review_request_id": record.review_request.review_request_id,
    }
    await repo.accept_action(record.run_id, action)
    replacement = AgentRunner(runner.agent, repo, runner.files)
    stream = await replacement.retry(record.run_id)
    async for _ in stream:
        pass
    assert (await repo.get(record.run_id)).review_request.review_request_id != action[
        "review_request_id"
    ]
    await replacement.close()


@pytest.mark.asyncio
async def test_failed_validator_can_retry_same_revision(tmp_path):
    from langchain.agents import create_agent

    runner, repo, record, action = await setup(tmp_path)
    subagents, _ = specs()
    for sub in subagents:
        if sub["name"] == "file-validation":
            sub["runnable"] = create_agent(FixedModel(reply="bad-json"))
    runner.agent = create_document_agent(
        FixedModel(), runner.files, runner.agent.checkpointer, subagent_specs=subagents
    )
    edit = {k: v for k, v in action.items() if k not in {"action", "message"}}
    stream = await runner.submit_action(
        record.run_id, {**edit, "action": "edit", "edits": {"segment-0001": "수정본"}}
    )
    async for _ in stream:
        pass
    assert (await repo.get(record.run_id)).status == RunStatus.FAILED
    subagents, _ = specs()
    runner.agent = create_document_agent(
        FixedModel(), runner.files, runner.agent.checkpointer, subagent_specs=subagents
    )
    stream = await runner.retry(record.run_id)
    async for _ in stream:
        pass
    record = await repo.get(record.run_id)
    assert record.status == RunStatus.WAITING_FOR_REVIEW, record.error
    assert record.review_request.revision == 2
    assert record.review_request.segments[0].first_translation == "수정본"
