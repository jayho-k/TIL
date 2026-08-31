import pytest

from app.agents.registry import AgentRegistry


class StubRunner:
    async def run(self, message: str, thread_id: str) -> str:
        return f"{thread_id}:{message}"


def test_registry_resolves_registered_runner():
    runner = StubRunner()
    registry = AgentRegistry({"general": runner})

    assert registry.get("general") is runner


def test_registry_rejects_duplicate_registration():
    registry = AgentRegistry({"general": StubRunner()})

    with pytest.raises(ValueError, match="already registered"):
        registry.register("general", StubRunner())


def test_registry_rejects_unknown_agent():
    registry = AgentRegistry()

    with pytest.raises(KeyError):
        registry.get("missing")

