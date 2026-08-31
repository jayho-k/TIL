from app.prompts.assembly import build_system_prompt
from app.prompts.registry import PromptRegistry


def test_build_prompt_places_shared_policy_before_agent_prompt(tmp_path):
    registry = PromptRegistry(
        root=tmp_path,
        paths={"shared.safety": "shared.md", "general.system": "general.md"},
    )
    (tmp_path / "shared.md").write_text("SAFE", encoding="utf-8")
    (tmp_path / "general.md").write_text("GENERAL", encoding="utf-8")

    assert build_system_prompt(registry, "general") == "SAFE\n\nGENERAL"


def test_registry_rejects_unknown_prompt_key(tmp_path):
    registry = PromptRegistry(root=tmp_path, paths={})

    try:
        registry.read("missing")
    except KeyError as exc:
        assert exc.args == ("missing",)
    else:
        raise AssertionError("unknown prompt key must fail")

