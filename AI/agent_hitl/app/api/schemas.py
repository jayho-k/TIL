from pydantic import BaseModel, Field

from app.domain.models import ReviewRequest, RunStatus


class RunStatusResponse(BaseModel):
    run_id: str
    status: RunStatus
    review_request: ReviewRequest | None = None
    download_url: str | None = None
    history: list[dict] = Field(default_factory=list)
    error: str | None = None
