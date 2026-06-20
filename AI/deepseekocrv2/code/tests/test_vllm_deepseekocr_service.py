import sys
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.services.vllm_deepseekocr import AsyncDeepSeekOCRService, OCRImageInput


class FakeSamplingParams:
    def __init__(self, *, temperature, max_tokens):
        self.temperature = temperature
        self.max_tokens = max_tokens


class FakeEngine:
    async def generate(self, request, sampling_params, *, request_id):
        filename = request["multi_modal_data"]["image"].info["filename"]
        yield SimpleNamespace(outputs=[SimpleNamespace(text=f"ocr:{filename}")])


def make_item(index, filename):
    image = Image.new("RGB", (8, 8), color=(255, 255, 255))
    image.info["filename"] = filename
    return OCRImageInput(index=index, filename=filename, image=image)


def test_service_returns_results_sorted_by_input_index():
    service = AsyncDeepSeekOCRService(
        Settings(),
        engine=FakeEngine(),
        sampling_params_cls=FakeSamplingParams,
    )

    import asyncio

    results = asyncio.run(
        service.infer_batch(
            [make_item(1, "b.png"), make_item(0, "a.png")],
            prompt="<image>\nOCR",
            max_tokens=64,
            temperature=0,
        )
    )

    assert [item["index"] for item in results] == [0, 1]
    assert [item["text"] for item in results] == ["ocr:a.png", "ocr:b.png"]


def test_service_records_page_error_without_raising():
    class FailingEngine:
        async def generate(self, request, sampling_params, *, request_id):
            raise RuntimeError("boom")
            yield

    service = AsyncDeepSeekOCRService(
        Settings(),
        engine=FailingEngine(),
        sampling_params_cls=FakeSamplingParams,
    )

    import asyncio

    results = asyncio.run(
        service.infer_batch(
            [make_item(0, "bad.png")],
            prompt="<image>\nOCR",
            max_tokens=64,
            temperature=0,
        )
    )

    assert results[0]["index"] == 0
    assert results[0]["text"] == ""
    assert "RuntimeError" in results[0]["error"]
