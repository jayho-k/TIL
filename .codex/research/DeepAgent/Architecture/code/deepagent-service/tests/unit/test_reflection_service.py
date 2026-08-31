from app.models.reflection_job import ReflectionJobStatus
from app.repositories.reflection_job_repository import InMemoryReflectionJobRepository
from app.services.reflection_service import ReflectionService


def test_created_reflection_job_is_pending():
    service = ReflectionService(InMemoryReflectionJobRepository())

    job = service.create_job(subject="daily")

    assert job.subject == "daily"
    assert job.status is ReflectionJobStatus.PENDING
    assert service.get_job(job.id) == job


def test_run_job_records_result():
    service = ReflectionService(InMemoryReflectionJobRepository())
    job = service.create_job(subject="daily")

    completed = service.run_job(job.id, lambda subject: f"reflected:{subject}")

    assert completed.status is ReflectionJobStatus.COMPLETED
    assert completed.result == "reflected:daily"

