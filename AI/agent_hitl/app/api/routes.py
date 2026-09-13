from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

from app.api.schemas import RunStatusResponse
from app.domain.models import ReviewDecision, RunStatus
from app.domain.revisions import ReviewAction
from app.runs.repository import ReviewConflict, RunNotFound
from app.storage.files import InvalidTextEncoding

router = APIRouter()


@router.post("/runs")
async def start_run(request: Request, file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(400, "TXT 파일만 지원합니다.")
    content = await file.read()
    try:
        text = content.decode("utf-8")
        record = await request.app.state.runner.create_run(content)
    except (UnicodeDecodeError, InvalidTextEncoding) as exc:
        raise HTTPException(400, "UTF-8 TXT만 지원합니다.") from exc
    return EventSourceResponse(await request.app.state.runner.launch_start(record.run_id, text))


@router.post("/runs/{run_id}/resume")
async def resume_run(run_id: str, decision: ReviewDecision, request: Request):
    try:
        generator = await request.app.state.runner.legacy_action(run_id, decision)
        return EventSourceResponse(generator)
    except RunNotFound as exc:
        raise HTTPException(404, "run을 찾을 수 없습니다.") from exc
    except ReviewConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/runs/{run_id}/review-actions")
async def review_action(run_id: str, action: ReviewAction, request: Request):
    try:
        stream = await request.app.state.runner.submit_action(run_id, action.model_dump())
        return EventSourceResponse(stream)
    except RunNotFound as exc:
        raise HTTPException(404, "run을 찾을 수 없습니다.") from exc
    except ReviewConflict as exc:
        raise HTTPException(409, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/runs/{run_id}/retry")
async def retry_run(run_id: str, request: Request):
    try:
        return EventSourceResponse(await request.app.state.runner.retry(run_id))
    except RunNotFound as exc:
        raise HTTPException(404, "run을 찾을 수 없습니다.") from exc
    except (ReviewConflict, ValueError, OSError) as exc:
        raise HTTPException(409, str(exc)) from exc


@router.get("/runs/{run_id}", response_model=RunStatusResponse)
async def get_run(run_id: str, request: Request):
    try:
        record = await request.app.state.runner.get_status(run_id)
    except RunNotFound as exc:
        raise HTTPException(404, "run을 찾을 수 없습니다.") from exc
    return RunStatusResponse(
        run_id=run_id,
        status=record.status,
        review_request=record.review_request,
        history=record.history,
        error=record.error,
        download_url=(f"/runs/{run_id}/download" if record.status == RunStatus.COMPLETED else None),
    )


@router.get("/runs/{run_id}/download")
async def download_run(run_id: str, request: Request):
    try:
        record = await request.app.state.repository.get(run_id)
    except RunNotFound as exc:
        raise HTTPException(404, "run을 찾을 수 없습니다.") from exc
    if record.status != RunStatus.COMPLETED or not record.output_path:
        raise HTTPException(409, "아직 다운로드할 결과가 없습니다.")
    return FileResponse(record.output_path, filename=f"{run_id}-translated.txt")
