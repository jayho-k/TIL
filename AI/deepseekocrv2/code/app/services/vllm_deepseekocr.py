import asyncio
import time
from dataclasses import dataclass
from typing import Any

from PIL import Image

from app.config import Settings


@dataclass(frozen=True)
class OCRImageInput:
    index: int
    filename: str
    image: Image.Image


class AsyncDeepSeekOCRService:
    def __init__(
        self,
        settings: Settings,
        *,
        engine: Any | None = None,
        sampling_params_cls: Any | None = None,
    ) -> None:
        self._settings = settings
        self._engine: Any | None = engine
        self._sampling_params_cls: Any | None = sampling_params_cls
        self._semaphore = asyncio.Semaphore(1)

    async def load(self) -> None:
        from vllm import SamplingParams
        from vllm.engine.arg_utils import AsyncEngineArgs
        from vllm.v1.engine.async_llm import AsyncLLM

        self._sampling_params_cls = SamplingParams
        engine_args = AsyncEngineArgs(
            model=self._settings.model_path,
            tokenizer=self._settings.model_path,
            dtype=self._settings.dtype,
            gpu_memory_utilization=self._settings.gpu_memory_utilization,
            limit_mm_per_prompt={"image": 1},
        )
        self._engine = AsyncLLM.from_engine_args(engine_args)

    async def infer_batch(
        self,
        images: list[OCRImageInput],
        *,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> list[dict[str, Any]]:
        if self._engine is None or self._sampling_params_cls is None:
            raise RuntimeError("DeepSeekOCR2 service is not loaded")

        async with self._semaphore:
            tasks = [
                self._infer_one(item, prompt, max_tokens, temperature)
                for item in images
            ]
            results = await asyncio.gather(*tasks)

        return sorted(results, key=lambda item: item["index"])

    async def _infer_one(
        self,
        item: OCRImageInput,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        sampling_params = self._sampling_params_cls(
            temperature=temperature,
            max_tokens=max_tokens,
        )
        request = {
            "prompt": prompt,
            "multi_modal_data": {"image": item.image},
        }
        request_id = f"deepseekocr2-{item.index}-{time.time_ns()}"

        final_output = None
        try:
            async for output in self._engine.generate(
                request,
                sampling_params,
                request_id=request_id,
            ):
                final_output = output
            text = self._extract_text(final_output)
            error = None
        except Exception as exc:
            text = ""
            error = repr(exc)

        return {
            "index": item.index,
            "filename": item.filename,
            "text": text,
            "elapsed_ms": int((time.perf_counter() - started) * 1000),
            "error": error,
        }

    @staticmethod
    def _extract_text(output: Any) -> str:
        if output is None:
            return ""
        outputs = getattr(output, "outputs", None)
        if not outputs:
            return ""
        return getattr(outputs[0], "text", "") or ""
