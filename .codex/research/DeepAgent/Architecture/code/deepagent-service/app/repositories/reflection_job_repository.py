from typing import Protocol

from app.models.reflection_job import ReflectionJob


class ReflectionJobRepository(Protocol):
    def add(self, job: ReflectionJob) -> None: ...

    def get(self, job_id: str) -> ReflectionJob | None: ...

    def save(self, job: ReflectionJob) -> None: ...


class InMemoryReflectionJobRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, ReflectionJob] = {}

    def add(self, job: ReflectionJob) -> None:
        if job.id in self._jobs:
            raise ValueError(f"reflection job already exists: {job.id}")
        self._jobs[job.id] = job

    def get(self, job_id: str) -> ReflectionJob | None:
        return self._jobs.get(job_id)

    def save(self, job: ReflectionJob) -> None:
        if job.id not in self._jobs:
            raise KeyError(job.id)
        self._jobs[job.id] = job

