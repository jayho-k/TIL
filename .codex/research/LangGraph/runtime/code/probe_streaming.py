"""Inspect stream payloads, projections and async generator cancellation."""

import asyncio
import json
from importlib.metadata import version

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    value: int
    messages: Annotated[list, add_messages]


def make_graph(action=None, *, saver=None):
    builder = StateGraph(State)
    builder.add_node("work", action or (lambda state: {"value": state["value"] + 1}))
    builder.add_edge(START, "work")
    builder.add_edge("work", END)
    return builder.compile(checkpointer=saver)


def probe_modes():
    graph = make_graph()
    events = list(graph.stream({"value": 0}, stream_mode=["updates", "values"]))
    modes = [mode for mode, _ in events]
    updates = [payload for mode, payload in events if mode == "updates"]
    values = [payload for mode, payload in events if mode == "values"]
    assert updates == [{"work": {"value": 1}}]
    assert values[0]["value"] == 0 and values[-1]["value"] == 1
    assert graph.invoke({"value": 0})["value"] == values[-1]["value"]
    return {"modes": modes, "updates": updates, "values": values,
            "invoke_matches_last_value": True}


def probe_custom_and_messages():
    def work(state: State):
        get_stream_writer()({"progress": "working"})
        return {"value": 1, "messages": [AIMessage(content="complete message", id="a1")]}

    graph = make_graph(work)
    events = list(graph.stream({"value": 0}, stream_mode=["custom", "messages", "values"]))
    custom = [payload for mode, payload in events if mode == "custom"]
    messages = [payload for mode, payload in events if mode == "messages"]
    assert custom == [{"progress": "working"}]
    assert len(messages) == 1 and messages[0][0].content == "complete message"
    assert messages[0][1]["langgraph_node"] == "work"
    last_values = [payload for mode, payload in events if mode == "values"][-1]
    assert last_values["value"] == 1
    return {"event_modes": [mode for mode, _ in events], "custom": custom,
            "message_type": type(messages[0][0]).__name__,
            "message_node": messages[0][1]["langgraph_node"],
            "message_content": messages[0][0].content, "final_value": last_values["value"]}


def probe_v2():
    events = list(make_graph().stream({"value": 0}, stream_mode=["updates", "values"], version="v2"))
    assert all(isinstance(event, dict) and {"type", "ns", "data"} <= set(event) for event in events)
    assert all(event["ns"] == () for event in events)
    assert events[-1]["type"] == "values" and events[-1]["data"]["value"] == 1
    return {"event_fields": [sorted(event) for event in events],
            "event_types": [event["type"] for event in events], "root_namespace": []}


def probe_tasks_checkpoints():
    graph = make_graph(saver=InMemorySaver())
    config = {"configurable": {"thread_id": "events"}}
    events = list(graph.stream({"value": 0}, config, stream_mode=["tasks", "checkpoints"], durability="sync"))
    tasks = [payload for mode, payload in events if mode == "tasks"]
    checkpoints = [payload for mode, payload in events if mode == "checkpoints"]
    assert len(tasks) >= 2 and len(checkpoints) >= 2
    assert graph.get_state(config).values["value"] == 1
    return {"task_events": len(tasks), "checkpoint_events": len(checkpoints),
            "task_payload_keys": sorted(set().union(*(set(payload) for payload in tasks))),
            "checkpoint_payload_keys": sorted(checkpoints[-1]), "saved_final_value": 1}


async def probe_close():
    cancelled = asyncio.Event()
    finished = []

    async def work(state: State):
        get_stream_writer()({"progress": "started"})
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            raise
        finished.append("returned")
        return {"value": 1}

    graph = make_graph(work, saver=InMemorySaver())
    config = {"configurable": {"thread_id": "close"}}
    stream = graph.astream({"value": 0}, config, stream_mode="custom", durability="sync")
    first = await asyncio.wait_for(anext(stream), 3)
    assert first == {"progress": "started"}
    await asyncio.wait_for(stream.aclose(), 3)
    await asyncio.wait_for(cancelled.wait(), 3)
    state = await graph.aget_state(config)
    assert finished == [] and state.values["value"] == 0
    return {"first_event": first, "node_cancelled": True, "node_returned": False,
            "saved_value": state.values["value"], "next": list(state.next)}


def probe_subgraph_namespace():
    child = make_graph()
    builder = StateGraph(State)
    builder.add_node("child", child)
    builder.add_edge(START, "child")
    builder.add_edge("child", END)
    events = list(builder.compile().stream({"value": 0}, stream_mode="updates", subgraphs=True))
    nested = [(ns, value) for ns, value in events if ns]
    root = [(ns, value) for ns, value in events if not ns]
    assert nested and root
    assert nested[0][0][0].startswith("child:")
    return {"nested_namespace_has_child_task": True, "root_namespace": [],
            "nested_payload_nodes": sorted(nested[0][1]), "parent_payload_nodes": sorted(root[-1][1])}


def main():
    observations = {"updates_and_values": probe_modes(), "custom_and_node_messages": probe_custom_and_messages(),
                    "v2_shape": probe_v2(), "tasks_and_checkpoints": probe_tasks_checkpoints(),
                    "async_close": asyncio.run(probe_close()), "subgraph_namespaces": probe_subgraph_namespace()}
    print(json.dumps({"langgraph_version": version("langgraph"),
                      "results": {name: {"status": "passed", "observed": value}
                                  for name, value in observations.items()}}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
