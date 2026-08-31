from pydantic import BaseModel, ConfigDict, Field

from app.models.reflection_job import ReflectionJobStatus


class ReflectionJobCreate(BaseModel):
    subject: str = Field(min_length=1)


class ReflectionJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    subject: str
    status: ReflectionJobStatus
    result: str | None = None
    error: str | None = None

