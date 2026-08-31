from typing import Protocol


class AgentRunner(Protocol):
    async def run(self, message: str, thread_id: str) -> str: ...

