import hashlib
import json

from redis.asyncio import Redis

from app.domain.models import ReviewDecision, ReviewRequest, RunRecord, RunStatus


class RunNotFound(KeyError):
    pass


class ReviewConflict(RuntimeError):
    pass


class RedisRunRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def _key(run_id: str) -> str:
        return f"agent-hitl:run:{run_id}"

    async def create(self, record: RunRecord) -> None:
        await self.redis.set(self._key(record.run_id), record.model_dump_json())

    async def get(self, run_id: str) -> RunRecord:
        raw = await self.redis.get(self._key(run_id))
        if raw is None:
            raise RunNotFound(run_id)
        return RunRecord.model_validate_json(raw)

    async def save(self, record: RunRecord) -> None:
        await self.redis.set(self._key(record.run_id), record.model_dump_json())

    async def set_status(self, run_id: str, status: RunStatus, **updates) -> RunRecord:
        record = await self.get(run_id)
        record = record.model_copy(update={"status": status, **updates})
        await self.save(record)
        return record

    async def set_review(self, run_id: str, request: ReviewRequest) -> RunRecord:
        return await self.set_status(
            run_id,
            RunStatus.WAITING_FOR_REVIEW,
            review_request=request,
        )

    async def accept_decision(self, run_id: str, decision: ReviewDecision) -> bool:
        record = await self.get(run_id)
        if record.review_request is None:
            raise ReviewConflict("대기 중인 검수 요청이 없습니다.")
        if decision.review_request_id != record.review_request.review_request_id:
            raise ReviewConflict("review_request_id가 현재 요청과 다릅니다.")
        if decision.revision != record.review_request.revision:
            raise ReviewConflict("오래된 revision입니다.")
        digest = hashlib.sha256(
            json.dumps(decision.model_dump(mode="json"), sort_keys=True).encode()
        ).hexdigest()
        if record.decision_hash:
            if record.decision_hash == digest:
                return False
            raise ReviewConflict("이미 다른 결정으로 재개된 요청입니다.")
        await self.set_status(
            run_id,
            RunStatus.RESUMING,
            decision_hash=digest,
        )
        return True
