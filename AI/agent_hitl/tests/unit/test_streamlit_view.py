from pathlib import Path

from streamlit.testing.v1 import AppTest

from streamlit_app.client import AgentApiClient


def test_unsaved_edits_disable_approval(monkeypatch):
    record = {
        "status": "WAITING_FOR_REVIEW",
        "history": [],
        "error": None,
        "review_request": {
            "revision": 1,
            "review_request_id": "review",
            "snapshot_hash": "hash",
            "history": [],
            "segments": [
                {
                    "segment_id": "s1",
                    "original_text": "Hi",
                    "first_translation": "안녕",
                    "validated_translation": "안녕하세요",
                    "validation_note": "존댓말",
                }
            ],
        },
    }
    monkeypatch.setattr(AgentApiClient, "status", lambda self, run_id: record)
    app = AppTest.from_file(str(Path("streamlit_app/main.py").resolve()), default_timeout=10)
    app.session_state["run_id"] = "test-run"
    app.run()
    assert not app.exception
    approval = next(button for button in app.button if button.label == "현재 버전 최종 확정")
    assert not approval.disabled
    app.text_area[0].set_value("수정").run()
    assert not app.exception
    approval = next(button for button in app.button if button.label == "현재 버전 최종 확정")
    assert approval.disabled
