from collections.abc import Mapping

from app.agents.common.contracts import AgentRunner


class AgentRegistry:
    def __init__(self, agents: Mapping[str, AgentRunner] | None = None) -> None:
        self._agents = dict(agents or {})

    def register(self, name: str, runner: AgentRunner) -> None:
        if name in self._agents:
            raise ValueError(f"agent already registered: {name}")
        self._agents[name] = runner

    def get(self, name: str) -> AgentRunner:
        try:
            return self._agents[name]
        except KeyError:
            raise KeyError(name) from None

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._agents))

