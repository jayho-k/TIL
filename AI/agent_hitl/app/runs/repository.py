from redis.asyncio import Redis
from redis.exceptions import WatchError

from app.domain.models import ReviewRequest, RunRecord, RunStatus
from app.domain.revisions import content_hash, validate_action


class RunNotFound(KeyError):
    pass


class ReviewConflict(RuntimeError):
    pass


class RedisRunRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _key(run_id):
        return f"agent-hitl:run:{run_id}"

    async def create(self, record):
        await self.redis.set(self._key(record.run_id), record.model_dump_json())

    async def get(self, run_id):
        raw = await self.redis.get(self._key(run_id))
        if raw is None:
            raise RunNotFound(run_id)
        return RunRecord.model_validate_json(raw)

    async def mutate(self, run_id, change):
        key = self._key(run_id)
        for _ in range(20):
            async with self.redis.pipeline(transaction=True) as pipe:
                try:
                    await pipe.watch(key)
                    raw = await pipe.get(key)
                    if raw is None:
                        raise RunNotFound(run_id)
                    record = RunRecord.model_validate_json(raw)
                    result = change(record)
                    pipe.multi()
                    pipe.set(key, record.model_dump_json())
                    await pipe.execute()
                    return result
                except WatchError:
                    continue
        raise ReviewConflict("동시 요청이 많습니다. 다시 시도하세요.")

    async def set_status(self, run_id, status, **updates):
        def change(record):
            record.status = status
            for key, value in updates.items():
                setattr(record, key, value)
            return record

        return await self.mutate(run_id, change)

    async def accept_action(self, run_id, raw):
        def change(record):
            digest = content_hash(raw)
            command_id = raw["command_id"]
            previous = record.commands.get(command_id)
            if previous:
                if previous["hash"] != digest:
                    raise ReviewConflict("같은 command_id의 내용이 다릅니다.")
                return False
            request = record.review_request
            if record.status != RunStatus.WAITING_FOR_REVIEW or request is None:
                raise ReviewConflict("검수 입력을 받을 수 있는 상태가 아닙니다.")
            if (
                request.review_request_id != raw["review_request_id"]
                or request.revision != raw["revision"]
                or request.snapshot_hash != raw["snapshot_hash"]
            ):
                raise ReviewConflict("오래된 검수 회차 또는 revision입니다.")
            action = validate_action(request, raw)
            record.active_command = action.model_dump()
            record.commands[command_id] = {"hash": digest, "body": raw, "status": "accepted"}
            record.status = RunStatus.RESUMING
            record.error = None
            return True

        return await self.mutate(run_id, change)

    async def finish(self, run_id, status, **updates):
        def change(record):
            if record.active_command:
                command_id = record.active_command["command_id"]
                record.commands[command_id]["status"] = "completed"
            record.active_command = None
            record.status = status
            record.error = None
            for key, value in updates.items():
                setattr(record, key, value)
            return record

        return await self.mutate(run_id, change)

    async def set_review(self, run_id, request: ReviewRequest, interrupt_id=None):
        return await self.finish(
            run_id,
            RunStatus.WAITING_FOR_REVIEW,
            review_request=request,
            interrupt_id=interrupt_id,
            history=request.history,
        )
