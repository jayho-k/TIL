from collections.abc import AsyncIterator

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langgraph.checkpoint.memory import InMemorySaver

from app.agents.factory import create_chat_agent
from app.agents.source import LangGraphEventSource
from app.streaming.projector import StreamEventProjector


class FakeGraph:
    def __init__(self) -> None:
        self.items = [
            {"type": "messages", "data": "first"},
            {"type": "updates", "data": "second"},
        ]
        self.input = None
        self.config = None
        self.kwargs = None

    async def astream(self, input, *, config, **kwargs) -> AsyncIterator[object]:
        self.input = input
        self.config = config
        self.kwargs = kwargs
        for item in self.items:
            yield item


@pytest.mark.asyncio
async def test_source_passes_thread_and_v2_modes() -> None:
    graph = FakeGraph()
    source = LangGraphEventSource(graph)

    items = [item async for item in source.stream("hello", "thread-1")]

    assert items == graph.items
    assert graph.input == {"messages": [{"role": "user", "content": "hello"}]}
    assert graph.config["configurable"]["thread_id"] == "thread-1"
    assert graph.kwargs == {
        "stream_mode": ["messages", "updates", "custom"],
        "version": "v2",
        "subgraphs": True,
    }


@pytest.mark.asyncio
async def test_real_deepagent_v2_messages_match_public_filter_without_network():
    class LocalModel(FakeListChatModel):
        def bind_tools(self, tools, **kwargs):
            return self

    graph = create_chat_agent(LocalModel(responses=["hello"]), InMemorySaver())
    projector = StreamEventProjector()
    parts = []
    async for raw in LangGraphEventSource(graph).stream("hi", "local-test"):
        parts.extend(event.data.get("text", "") for event in projector.project(raw))
    assert "".join(parts) == "hello"
