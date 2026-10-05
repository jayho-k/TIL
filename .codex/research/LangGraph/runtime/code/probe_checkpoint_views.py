"""Inspect persisted state, history and successful pending writes without a model."""

import json
from importlib.metadata import version
from operator import add
from threading import Event
from typing import Annotated

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class State(TypedDict):
    question: str
    records: Annotated[list[str], add]
    count: int


class Output(TypedDict):
    count: int


def probe_memory_and_history():
    calls = []
    saver = InMemorySaver()

    def record(state: State):
        calls.append(state["question"])
        return {"records": [state["question"]], "count": len(state["records"]) + 1}

    builder = StateGraph(State, output_schema=Output)
    builder.add_node("record", record)
    builder.add_edge(START, "record")
    builder.add_edge("record", END)
    graph = builder.compile(checkpointer=saver)
    config = {"configurable": {"thread_id": "conversation"}}
    before = graph.get_state(config)
    assert before.values == {} and before.next == ()
    one = graph.invoke({"question": "one"}, config, durability="sync")
    saved_one = graph.get_state(config)
    two = graph.invoke({"question": "two"}, config, durability="sync")
    latest = graph.get_state(config)
    assert one == {"count": 1} and two == {"count": 2}
    assert latest.values["records"] == ["one", "two"]
    assert latest.next == () and latest.values["question"] == "two"
    count_before_reads = len(calls)
    history = list(graph.get_state_history(config, limit=3))
    historical = graph.get_state(saved_one.config)
    assert historical.values["records"] == ["one"]
    assert len(calls) == count_before_reads
    assert len(history) == 3
    other = {"configurable": {"thread_id": "other-conversation"}}
    other_output = graph.invoke({"question": "other"}, other, durability="sync")
    assert other_output == {"count": 1}
    assert graph.get_state(other).values["records"] == ["other"]
    checkpoint = saver.get_tuple(config).checkpoint
    return {"before_first_run": {"values": before.values, "next": list(before.next)},
            "first_output": one, "second_output": two,
            "latest_values": latest.values, "latest_next": list(latest.next),
            "specified_checkpoint_values": historical.values,
            "history": [{"step": state.metadata["step"], "source": state.metadata["source"],
                         "next": list(state.next), "values": state.values} for state in history],
            "reads_execute_user_nodes": False,
            "other_thread_values": graph.get_state(other).values,
            "checkpoint_keys": sorted(checkpoint), "checkpoint_format_version": checkpoint["v"]}


def probe_pending_writes():
    saved_a = Event()

    class NotifyingSaver(InMemorySaver):
        def put_writes(self, config, writes, task_id, task_path=""):
            super().put_writes(config, writes, task_id, task_path)
            if any(channel == "records" and value == ["a"] for channel, value in writes):
                saved_a.set()

    saver = NotifyingSaver()
    calls = {"a": 0, "b": 0}

    def a(state: State):
        calls["a"] += 1
        return {"records": ["a"]}

    def b(state: State):
        calls["b"] += 1
        if calls["b"] == 1:
            if not saved_a.wait(5):
                raise AssertionError("A successful write was not saved")
            raise ValueError("b failed")
        return {"records": ["b"]}

    builder = StateGraph(State)
    for name, action in [("a", a), ("b", b)]:
        builder.add_node(name, action)
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    graph = builder.compile(checkpointer=saver)
    config = {"configurable": {"thread_id": "pending"}}
    try:
        graph.invoke({"question": "q"}, config, durability="sync")
    except ValueError as error:
        assert str(error) == "b failed"
    else:
        raise AssertionError("B must fail its first invocation")
    latest = graph.get_state(config)
    stored = saver.get_tuple(config)
    explicit = graph.get_state(stored.config)
    assert latest.values["records"] == ["a"]
    assert explicit.values["records"] == []
    assert latest.next == ("b",)
    final = graph.invoke(None, config, durability="sync")
    assert calls == {"a": 1, "b": 2}
    assert final["records"] == ["a", "b"]
    return {"latest_view": {"values": latest.values, "next": list(latest.next)},
            "specified_checkpoint_view": {"values": explicit.values, "next": list(explicit.next)},
            "pending_write_channels": sorted(set(channel for _, channel, _ in stored.pending_writes)),
            "calls_after_recovery": calls, "final_values": final}


def probe_no_checkpointer():
    builder = StateGraph(State)
    builder.add_node("noop", lambda state: {})
    builder.add_edge(START, "noop")
    graph = builder.compile()
    try:
        graph.get_state({"configurable": {"thread_id": "missing"}})
    except ValueError as error:
        assert str(error) == "No checkpointer set"
        return {"error": str(error)}
    raise AssertionError("get_state requires a checkpointer")


def main():
    probes = {"memory_history_and_output": probe_memory_and_history,
              "pending_views_and_recovery": probe_pending_writes,
              "missing_checkpointer": probe_no_checkpointer}
    results = {name: {"status": "passed", "observed": probe()} for name, probe in probes.items()}
    print(json.dumps({"langgraph_version": version("langgraph"),
                      "checkpoint_version": version("langgraph-checkpoint"),
                      "results": results}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
