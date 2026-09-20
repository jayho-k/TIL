from collections.abc import AsyncIterator
from contextlib import aclosing
from typing import Any, Protocol


class AgentEventSource(Protocol):
    def stream(self, message: str, thread_id: str) -> AsyncIterator[Any]: ...


class LangGraphEventSource:
    def __init__(self, graph: Any) -> None:
        self._graph = graph

    async def stream(self, message: str, thread_id: str) -> AsyncIterator[Any]:
        iterator = self._graph.astream(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": thread_id}},
            stream_mode=["messages", "updates", "custom"],
            version="v2",
            subgraphs=True,
        )
        async with aclosing(iterator):
            async for item in iterator:
                yield item
