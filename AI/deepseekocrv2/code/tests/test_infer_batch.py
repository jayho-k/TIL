import io
import sys
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import create_app


class FakeOCRService:
    async def infer_batch(self, images, *, prompt, max_tokens, temperature):
        return [
            {
                "index": item.index,
                "filename": item.filename,
                "text": f"text-{item.index}-{item.filename}",
                "elapsed_ms": 10 + item.index,
                "error": None,
            }
            for item in images
        ]


def make_png(name="page.png"):
    image = Image.new("RGB", (8, 8), color=(255, 255, 255))
    data = io.BytesIO()
    image.save(data, format="PNG")
    data.seek(0)
    return name, data, "image/png"


def test_infer_batch_returns_ordered_results():
    app = create_app(load_model=False)
    app.state.ocr_service = FakeOCRService()

    with TestClient(app) as client:
        response = client.post(
            "/infer/batch",
            files=[
                ("files", make_png("page_002.png")),
                ("files", make_png("page_001.png")),
            ],
            data={"max_tokens": "128", "temperature": "0"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    assert [item["index"] for item in body["results"]] == [0, 1]
    assert [item["filename"] for item in body["results"]] == [
        "page_002.png",
        "page_001.png",
    ]
    assert [item["text"] for item in body["results"]] == [
        "text-0-page_002.png",
        "text-1-page_001.png",
    ]
    assert isinstance(body["elapsed_ms"], int)


def test_infer_batch_rejects_non_image_file():
    app = create_app(load_model=False)
    app.state.ocr_service = FakeOCRService()

    with TestClient(app) as client:
        response = client.post(
            "/infer/batch",
            files=[("files", ("bad.txt", io.BytesIO(b"not-image"), "text/plain"))],
        )

    assert response.status_code == 400
    assert "not a valid image" in response.json()["detail"]
