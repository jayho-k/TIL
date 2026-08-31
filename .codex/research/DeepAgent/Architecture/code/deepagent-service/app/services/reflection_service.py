from collections.abc import Callable
from uuid import uuid4

from app.core.exceptions import ResourceNotFoundError
from app.models.reflection_job import ReflectionJob
from app.repositories.reflection_job_repository import ReflectionJobRepository


class ReflectionService:
    def __init__(self, repository: ReflectionJobRepository) -> None:
        self._repository = repository

    def create_job(self, subject: str) -> ReflectionJob:
        normalized = subject.strip()
        if not normalized:
            raise ValueError("subject must not be blank")
        job = ReflectionJob(id=str(uuid4()), subject=normalized)
        self._repository.add(job)
        return job

    def get_job(self, job_id: str) -> ReflectionJob:
        job = self._repository.get(job_id)
        if job is None:
            raise ResourceNotFoundError(f"reflection job not found: {job_id}")
        return job

    def run_job(self, job_id: str, reflect: Callable[[str], str]) -> ReflectionJob:
        job = self.get_job(job_id).running()
        self._repository.save(job)
        try:
            completed = job.complete(reflect(job.subject))
        except Exception as exc:
            failed = job.fail(str(exc))
            self._repository.save(failed)
            raise
        self._repository.save(completed)
        return completed

