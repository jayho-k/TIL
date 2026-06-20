import time
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from PIL import Image, UnidentifiedImageError

from app.schemas import BatchOCRResponse
from app.services.vllm_deepseekocr import OCRImageInput

router = APIRouter(prefix="/infer", tags=["infer"])


@router.post("/batch", response_model=BatchOCRResponse)
async def infer_batch(
    request: Request,
    files: Annotated[list[UploadFile], File()],
    prompt: Annotated[str | None, Form()] = None,
    max_tokens: Annotated[int | None, Form()] = None,
    temperature: Annotated[float | None, Form()] = None,
) -> BatchOCRResponse:
    started = time.perf_counter()
    settings = request.app.state.settings
    service = getattr(request.app.state, "ocr_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="OCR service is not loaded")

    images = await _read_images(files)
    result_items = await service.infer_batch(
        images,
        prompt=prompt or settings.default_prompt,
        max_tokens=max_tokens or settings.default_max_tokens,
        temperature=(
            settings.default_temperature if temperature is None else temperature
        ),
    )

    return BatchOCRResponse(
        count=len(result_items),
        elapsed_ms=int((time.perf_counter() - started) * 1000),
        results=result_items,
    )


async def _read_images(files: list[UploadFile]) -> list[OCRImageInput]:
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required")

    images: list[OCRImageInput] = []
    for index, file in enumerate(files):
        content = await file.read()
        try:
            import io

            image = Image.open(io.BytesIO(content)).convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename or 'file'} is not a valid image",
            ) from exc
        images.append(
            OCRImageInput(
                index=index,
                filename=file.filename or f"image_{index}",
                image=image,
            )
        )
    return images
