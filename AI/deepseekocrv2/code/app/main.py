from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.routers.infer import router as infer_router
from app.services.vllm_deepseekocr import AsyncDeepSeekOCRService


def create_app(*, load_model: bool = True) -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        if load_model:
            service = AsyncDeepSeekOCRService(settings)
            await service.load()
            app.state.ocr_service = service
        yield

    app = FastAPI(title="DeepSeekOCR2 vLLM Server", lifespan=lifespan)
    app.state.settings = settings
    app.include_router(infer_router)
    return app


app = create_app()
