from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from uuid import uuid4

from langgraph.types import Command

from app.api.sse import sse_event
from app.domain.models import ReviewDecision, ReviewRequest, RunRecord, RunStatus
from app.runs.repository import RedisRunRepository
from app.storage.files import LocalRunFileStore


class AgentRunner:
    def __init__(self, agent, repository: RedisRunRepository, files: LocalRunFileStore):
        self.agent = agent
        self.repository = repository
        self.files = files

    async def create_run(self, content: bytes) -> RunRecord:
        run_id = str(uuid4())
        input_path = self.files.save_input(run_id, content)
        record = RunRecord(
            run_id=run_id,
            thread_id=str(uuid4()),
            input_path=str(input_path),
        )
        await self.repository.create(record)
        return record

    async def start(self, run_id: str, content: str) -> AsyncIterator[dict[str, str]]:
        record = await self.repository.set_status(run_id, RunStatus.RUNNING)
        yield sse_event("progress", {"run_id": run_id, "stage": "starting"})
        config = {"configurable": {"thread_id": record.thread_id}}
        message = (
            f"run_id={run_id}\n다음 UTF-8 TXT를 한국어로 번역하세요.\n\n{content}"
        )
        try:
            result = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
                version="v2",
            )
            async for event in self._handle_result(run_id, result):
                yield event
        except Exception as exc:
            await self.repository.set_status(run_id, RunStatus.FAILED)
            yield sse_event(
                "failed",
                {"run_id": run_id, "code": "AGENT_ERROR", "message": str(exc)},
            )

    async def resume(
        self, run_id: str, decision: ReviewDecision
    ) -> AsyncIterator[dict[str, str]]:
        record = await self.repository.get(run_id)
        accepted = await self.repository.accept_decision(run_id, decision)
        if not accepted:
            if record.output_path:
                yield sse_event(
                    "completed",
                    {"run_id": run_id, "download_url": f"/runs/{run_id}/download"},
                )
            return
        yield sse_event("progress", {"run_id": run_id, "stage": "resuming"})
        config = {"configurable": {"thread_id": record.thread_id}}
        try:
            result = await self.agent.ainvoke(
                Command(resume=decision.model_dump(mode="json")),
                config=config,
                version="v2",
            )
            async for event in self._handle_result(run_id, result):
                yield event
        except Exception as exc:
            await self.repository.set_status(run_id, RunStatus.FAILED)
            yield sse_event(
                "failed",
                {"run_id": run_id, "code": "AGENT_ERROR", "message": str(exc)},
            )

    async def _handle_result(self, run_id: str, result: Any) -> AsyncIterator[dict[str, str]]:
        interrupts = getattr(result, "interrupts", ())
        if interrupts:
            request = ReviewRequest.model_validate(interrupts[0].value)
            await self.repository.set_review(run_id, request)
            yield sse_event(
                "hitl.required",
                {"run_id": run_id, "review_request": request.model_dump(mode="json")},
            )
            return

        output_path = self.files.root / run_id / "output.txt"
        if not Path(output_path).exists():
            value = getattr(result, "value", {})
            messages = value.get("messages", []) if isinstance(value, dict) else []
            last_text = messages[-1].text if messages else ""
            raise RuntimeError(
                f"Agent가 결과 파일을 생성하지 않았습니다. 마지막 응답: {last_text}"
            )
        await self.repository.set_status(
            run_id,
            RunStatus.COMPLETED,
            output_path=str(output_path),
        )
        yield sse_event(
            "completed",
            {"run_id": run_id, "download_url": f"/runs/{run_id}/download"},
        )
