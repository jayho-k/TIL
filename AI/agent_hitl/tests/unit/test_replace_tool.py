from pathlib import Path

from app.agents.tools import create_replace_tool
from app.storage.files import LocalRunFileStore


def test_replace_tool_does_not_accept_llm_supplied_run_id(tmp_path: Path):
    replace_tool = create_replace_tool(LocalRunFileStore(tmp_path))
    assert replace_tool.args == {}
