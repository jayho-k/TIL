from pathlib import Path
from types import SimpleNamespace

import pytest

from app.agents.tools import ReviewRequiredError, create_replace_tool
from app.domain.revisions import content_hash
from app.storage.files import LocalRunFileStore


def test_replace_tool_does_not_accept_llm_supplied_run_id(tmp_path: Path):
    replace_tool = create_replace_tool(LocalRunFileStore(tmp_path))
    assert replace_tool.args == {}


def approved_state():
    final = [{"segment_id": "segment-0001", "translated_text": "승인됨"}]
    current = {"segment-0001": "초안"}
    return dict(
        run_id="r",
        review_status="completed",
        final_translations=final,
        approved_revision=2,
        current_revision=2,
        approved_content_hash=content_hash(final),
        current_translations=current,
        input_hash=content_hash("Hello"),
        validation={"revision": 2, "input_hash": content_hash(current)},
    )


@pytest.mark.parametrize(
    "change",
    [
        {"review_status": "pending"},
        {"approved_revision": 1},
        {"approved_content_hash": "tampered"},
        {"input_hash": "different-file"},
    ],
)
def test_replace_checks_approval(tmp_path, change):
    files = LocalRunFileStore(tmp_path)
    files.save_input("r", b"Hello")
    tool = create_replace_tool(files)
    with pytest.raises(ReviewRequiredError):
        tool.func(SimpleNamespace(state={**approved_state(), **change}))
    assert not (tmp_path / "r" / "output.txt").exists()


def test_same_approval_reuses_file(tmp_path):
    files = LocalRunFileStore(tmp_path)
    files.save_input("r", b"Hello")
    tool = create_replace_tool(files)
    runtime = SimpleNamespace(state=approved_state())
    first = tool.func(runtime)
    before = (tmp_path / "r" / "output.txt").stat().st_mtime_ns
    assert tool.func(runtime) == first
    assert (tmp_path / "r" / "output.txt").stat().st_mtime_ns == before
