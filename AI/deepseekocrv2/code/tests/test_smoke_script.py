import subprocess
import sys
from pathlib import Path


def test_smoke_script_exposes_required_arguments():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "smoke_async_deepseekocr2.py"

    result = subprocess.run(
        [sys.executable, str(script), "--help"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--model-path" in result.stdout
    assert "--image" in result.stdout
    assert "--requests" in result.stdout
