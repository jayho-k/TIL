from dataclasses import dataclass, replace
from enum import StrEnum


class ReflectionJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ReflectionJob:
    id: str
    subject: str
    status: ReflectionJobStatus = ReflectionJobStatus.PENDING
    result: str | None = None
    error: str | None = None

    def running(self) -> "ReflectionJob":
        return replace(self, status=ReflectionJobStatus.RUNNING)

    def complete(self, result: str) -> "ReflectionJob":
        return replace(self, status=ReflectionJobStatus.COMPLETED, result=result, error=None)

    def fail(self, error: str) -> "ReflectionJob":
        return replace(self, status=ReflectionJobStatus.FAILED, error=error)

