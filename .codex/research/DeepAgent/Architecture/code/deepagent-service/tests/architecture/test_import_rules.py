import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[2]
APP_ROOT = PROJECT_ROOT / "app"


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_business_services_do_not_import_frameworks_or_vendor_sdks():
    forbidden = {
        "fastapi",
        "langgraph",
        "deepagents",
        "sqlalchemy",
        "redis",
        "qdrant_client",
        "minio",
    }

    for path in (APP_ROOT / "services").glob("*.py"):
        assert imported_roots(path).isdisjoint(forbidden), path


def test_agent_skills_are_owned_by_their_agents():
    expected = [
        APP_ROOT / "agents/general/skills/knowledge-search/SKILL.md",
        APP_ROOT / "agents/reflection/skills/daily-reflection/SKILL.md",
    ]

    assert all(path.is_file() for path in expected)
    assert not (PROJECT_ROOT / "skills").exists()


def test_storage_modules_share_one_directory():
    expected = {"postgres.py", "redis.py", "qdrant.py", "minio.py"}

    assert expected.issubset(path.name for path in (APP_ROOT / "storage").glob("*.py"))
    assert not (APP_ROOT / "db").exists()
