from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import ContainerDependency
from app.core.exceptions import ResourceNotFoundError
from app.schemas.reflection import ReflectionJobCreate, ReflectionJobResponse


router = APIRouter(prefix="/v1/reflection-jobs", tags=["reflection"])


@router.post(
    "",
    response_model=ReflectionJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_reflection_job(
    request: ReflectionJobCreate,
    container: ContainerDependency,
) -> ReflectionJobResponse:
    job = container.reflections.create_job(request.subject)
    return ReflectionJobResponse.model_validate(job)


@router.get("/{job_id}", response_model=ReflectionJobResponse)
async def get_reflection_job(
    job_id: str,
    container: ContainerDependency,
) -> ReflectionJobResponse:
    try:
        job = container.reflections.get_job(job_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReflectionJobResponse.model_validate(job)

