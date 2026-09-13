import asyncio
import json
from collections import defaultdict
from uuid import uuid4

from langgraph.types import Command

from app.api.sse import sse_event
from app.domain.models import ReviewRequest, RunRecord, RunStatus
from app.domain.review import resolve_review
from app.domain.revisions import content_hash
from app.runs.repository import ReviewConflict
from app.service.recovery import BUSY_STATUSES, inspect_checkpoint, load_file_snapshot


class AgentRunner:
    """Single-process execution ownership. SSE consumers never own the execution task."""

    def __init__(self, agent, repository, files):
        self.agent, self.repository, self.files = agent, repository, files
        self.tasks = {}
        self.locks = defaultdict(asyncio.Lock)

    @staticmethod
    def config(record):
        return {"configurable": {"thread_id": record.thread_id}, "recursion_limit": 200}

    async def create_run(self, content):
        run_id = str(uuid4())
        path = self.files.save_input(run_id, content)
        record = RunRecord(run_id=run_id, thread_id=str(uuid4()), input_path=str(path))
        await self.repository.create(record)
        return record

    async def launch_start(self, run_id, content):
        async with self.locks[run_id]:
            record = await self.repository.get(run_id)
            if record.status != RunStatus.CREATED:
                raise ReviewConflict("이미 시작한 작업입니다.")
            await self.repository.set_status(run_id, RunStatus.RUNNING)
            message = f"run_id={run_id}\n한국어로 번역하세요.\n\n{content}"
            return self.launch(record, {"messages": [{"role": "user", "content": message}]})

    async def start(self, run_id, content):
        stream = await self.launch_start(run_id, content)
        async for event in stream:
            yield event

    async def submit_action(self, run_id, raw):
        async with self.locks[run_id]:
            accepted = await self.repository.accept_action(run_id, raw)
            record = await self.repository.get(run_id)
            if not accepted:
                return self.status_events(record)
            if not record.interrupt_id:
                await self.repository.set_status(run_id, RunStatus.RECOVERY_REQUIRED)
                raise ReviewConflict("검수 중단 위치를 복원해야 합니다.")
            return self.launch(record, Command(resume={record.interrupt_id: raw}))

    async def legacy_action(self, run_id, decision):
        record = await self.repository.get(run_id)
        request = record.review_request
        if request is None or (
            decision.review_request_id != request.review_request_id
            or decision.revision != request.revision
        ):
            raise ReviewConflict("현재 검수 요청이 아닙니다.")
        final = resolve_review(request, decision)
        raw = {
            "command_id": f"legacy-{content_hash(decision.model_dump())}",
            "review_request_id": request.review_request_id,
            "revision": request.revision,
            "snapshot_hash": request.snapshot_hash,
        }
        if any(d.selected == "custom" for d in decision.decisions):
            raw.update(action="edit", edits={s.segment_id: s.translated_text for s in final})
        else:
            raw.update(action="approve", decisions=[d.model_dump() for d in decision.decisions])
        return await self.submit_action(run_id, raw)

    async def resume(self, run_id, decision):
        stream = await self.legacy_action(run_id, decision)
        async for event in stream:
            yield event

    def launch(self, record, input_value):
        existing = self.tasks.get(record.run_id)
        if existing and not existing.done():
            raise ReviewConflict("이미 실행 중입니다.")
        queue = asyncio.Queue()
        task = asyncio.create_task(self.execute(record, input_value, queue))
        self.tasks[record.run_id] = task
        return self.events(queue)

    async def events(self, queue):
        while True:
            event = await queue.get()
            if event is None:
                return
            yield event

    async def status_events(self, record):
        if record.status == RunStatus.WAITING_FOR_REVIEW:
            yield sse_event(
                "hitl.required",
                {
                    "run_id": record.run_id,
                    "review_request": record.review_request.model_dump(mode="json"),
                },
            )
        elif record.status == RunStatus.COMPLETED:
            yield sse_event(
                "completed",
                {"run_id": record.run_id, "download_url": f"/runs/{record.run_id}/download"},
            )
        elif record.status in {RunStatus.FAILED, RunStatus.RECOVERY_REQUIRED}:
            yield sse_event(
                "failed",
                {"run_id": record.run_id, "message": record.error, "status": record.status},
            )
        else:
            yield sse_event("progress", {"run_id": record.run_id, "status": record.status})

    async def execute(self, record, input_value, queue):
        run_id = record.run_id
        try:
            await queue.put(sse_event("progress", {"run_id": run_id, "stage": "running"}))
            result = await self.agent.ainvoke(input_value, self.config(record), version="v2")
            if result.interrupts:
                item = result.interrupts[0]
                request = ReviewRequest.model_validate(item.value)
                for entry in request.history[len(record.history) :]:
                    if entry["role"] == "assistant":
                        await queue.put(sse_event("review.message", {"run_id": run_id, **entry}))
                await self.repository.set_review(run_id, request, item.id)
            else:
                output = self.verified_output(record)
                await self.repository.finish(run_id, RunStatus.COMPLETED, output_path=str(output))
            async for event in self.status_events(await self.repository.get(run_id)):
                await queue.put(event)
        except Exception as exc:
            await self.repository.set_status(run_id, RunStatus.FAILED, error=str(exc))
            await queue.put(sse_event("failed", {"run_id": run_id, "message": str(exc)}))
        finally:
            await queue.put(None)

    def verified_output(self, record):
        directory = self.files.root / record.run_id
        output = directory / "output.txt"
        manifest = json.loads((directory / "output.manifest.json").read_text(encoding="utf-8"))
        if content_hash(output.read_text(encoding="utf-8")) != manifest["output_hash"]:
            raise ValueError("결과 파일 검증에 실패했습니다.")
        action = record.active_command
        if not action or action["action"] != "approve" or record.review_request is None:
            raise ValueError("승인 기록이 없습니다.")
        from app.domain.models import ReviewDecision

        final = resolve_review(
            record.review_request,
            ReviewDecision(
                review_request_id=action["review_request_id"],
                revision=action["revision"],
                decisions=action["decisions"],
            ),
        )
        if manifest["revision"] != action["revision"] or manifest["content_hash"] != content_hash(
            [s.model_dump() for s in final]
        ):
            raise ValueError("결과 파일이 현재 승인과 다릅니다.")
        return output

    async def get_status(self, run_id):
        async with self.locks[run_id]:
            record = await self.repository.get(run_id)
            if (
                self.tasks.get(run_id) and not self.tasks[run_id].done()
            ) or record.status not in BUSY_STATUSES:
                return record
            snapshot = await self.agent.aget_state(self.config(record), subgraphs=True)
            interrupts, _ = inspect_checkpoint(snapshot)
            _, nested, _ = await load_file_snapshot(self.agent, snapshot, record)
            if nested:
                interrupts, _ = inspect_checkpoint(nested)
            if interrupts:
                item = interrupts[0]
                request = ReviewRequest.model_validate(item.value)
                if (
                    not record.active_command
                    or record.active_command["review_request_id"] != request.review_request_id
                ):
                    return await self.repository.set_review(run_id, request, item.id)
            return await self.repository.set_status(
                run_id,
                RunStatus.RECOVERY_REQUIRED,
                error=record.error or "실행 복구 버튼으로 저장된 작업을 이어갈 수 있습니다.",
            )

    async def retry(self, run_id):
        async with self.locks[run_id]:
            if self.tasks.get(run_id) and not self.tasks[run_id].done():
                raise ReviewConflict("이미 실행 중입니다.")
            record = await self.repository.get(run_id)
            if record.status not in BUSY_STATUSES:
                raise ReviewConflict("복구 대상 작업이 아닙니다.")
            snapshot = await self.agent.aget_state(self.config(record), subgraphs=True)
            interrupts, state = inspect_checkpoint(snapshot)
            file_graph, nested, file_config = await load_file_snapshot(self.agent, snapshot, record)
            if nested:
                interrupts, state = inspect_checkpoint(nested)
            value = None
            if interrupts:
                item = interrupts[0]
                if (
                    record.active_command
                    and record.active_command["review_request_id"]
                    == item.value["review_request_id"]
                ):
                    value = Command(resume={item.id: record.active_command})
                else:
                    await self.repository.set_review(
                        run_id, ReviewRequest.model_validate(item.value), item.id
                    )
                    return self.status_events(await self.repository.get(run_id))
            elif not snapshot.next:
                output = self.verified_output(record)
                await self.repository.finish(run_id, RunStatus.COMPLETED, output_path=str(output))
                return self.status_events(await self.repository.get(run_id))
            elif (
                record.active_command
                and state
                and (
                    record.active_command["command_id"] not in state.get("applied_commands", [])
                    and state.get("pending_command") != record.active_command
                )
            ):
                raise ReviewConflict("명령 반영 여부를 확인할 수 없어 자동 재적용하지 않습니다.")
            if (
                not interrupts
                and nested
                and state.get("active_task")
                and "ResultCollectorMiddleware.before_model" in nested.next
            ):
                await file_graph.aupdate_state(
                    file_config,
                    {
                        "phase": "RETRYING",
                        "retry_task": state["active_task"],
                        "active_task": None,
                    },
                    as_node="ResultCollectorMiddleware.before_model",
                )
            await self.repository.set_status(run_id, RunStatus.RESUMING)
            return self.launch(record, value)

    async def close(self):
        if self.tasks:
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
