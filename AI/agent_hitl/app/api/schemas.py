from pydantic import BaseModel

from app.domain.models import ReviewRequest, RunStatus


class RunStatusResponse(BaseModel):
    run_id: str
    status: RunStatus
    review_request: ReviewRequest | None = None
    download_url: str | None = None
