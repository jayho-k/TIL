import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_project_requires_cpython_312_series() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    assert pyproject["project"]["requires-python"] == ">=3.12,<3.13"


def test_python_version_file_pins_312() -> None:
    assert (PROJECT_ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.12"
