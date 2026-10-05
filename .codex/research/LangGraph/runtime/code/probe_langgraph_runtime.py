"""Offline, source-study probes. No LLM calls, external stores, or app edits.

Run from the repository root with AI/agent_hitl's installed interpreter.
These assertions illustrate a pinned implementation, not the entire framework.
"""

from __future__ import annotations

import json
import time
from importlib.metadata import version
from operator import add
from typing import Annotated

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, RetryPolicy, interrupt
from typing_extensions import TypedDict


def chain(schema, node, *, saver=None, retry=None):
    builder = StateGraph(schema)
    builder.add_node("work", node, retry_policy=retry)
    builder.add_edge(START, "work")
    builder.add_edge("work", END)
    return builder.compile(checkpointer=saver)


def compiled_channels():
    class State(TypedDict):
        x: int

    builder = StateGraph(State)
    builder.add_node("a", lambda state: {"x": state["x"] + 1})
    builder.add_node("b", lambda state: {})
    builder.add_edge(START, "a")
    builder.add_edge("a", "b")
    builder.add_edge("b", END)
    graph = builder.compile()
    node = graph.nodes["b"]
    assert "x" in node.channels
    assert "x" not in node.triggers
    assert node.triggers == ["branch:to:b"]
    assert graph.invoke({"x": 0})["x"] == 1
    return {"b_reads": node.channels, "b_triggers": node.triggers}


def partial_updates():
    class State(TypedDict):
        items: Annotated[list[str], add]

    good = chain(State, lambda state: {"items": ["new"]})
    bad = chain(State, lambda state: {"items": state["items"] + ["new"]})
    good_value = good.invoke({"items": ["seed"]})["items"]
    bad_value = bad.invoke({"items": ["seed"]})["items"]
    assert good_value == ["seed", "new"]
    assert bad_value == ["seed", "seed", "new"]
    return {"partial": good_value, "full_accumulated_value": bad_value}


def step_visibility_and_aliases():
    class State(TypedDict):
        x: int
        nested: dict[str, int]
        observed: Annotated[list[int], add]

    views = []

    def a(state):
        views.append(state)
        return {"x": state["x"] + 1, "observed": [state["x"]]}

    def b(state):
        views.append(state)
        return {"observed": [state["x"]]}

    builder = StateGraph(State)
    builder.add_node("a", a)
    builder.add_node("b", b)
    builder.add_edge(START, "a")
    builder.add_edge(START, "b")
    builder.add_edge("a", END)
    builder.add_edge("b", END)
    output = builder.compile().invoke({"x": 0, "nested": {"count": 0}})
    assert output["observed"] == [0, 0]
    assert output["x"] == 1
    assert len(views) == 2
    assert views[0] is not views[1]
    assert views[0]["nested"] is views[1]["nested"]
    return {
        "both_read": output["observed"],
        "next_x": output["x"],
        "outer_dicts_distinct": True,
        "nested_object_shared": True,
    }


def concurrent_collision():
    class State(TypedDict):
        status: str

    builder = StateGraph(State)
    builder.add_node("a", lambda state: {"status": "a"})
    builder.add_node("b", lambda state: {"status": "b"})
    for name in ("a", "b"):
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    try:
        builder.compile().invoke({"status": "start"})
    except InvalidUpdateError:
        return {"result": "InvalidUpdateError (no last-finisher-wins)"}
    raise AssertionError("Expected conflicting LastValue writes to fail")


def short_term_memory():
    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph = chain(State, lambda state: {}, saver=InMemorySaver())
    config = {"configurable": {"thread_id": "stm"}}
    graph.invoke({"messages": [HumanMessage(content="first", id="u1")]}, config)
    second = graph.invoke(
        {"messages": [HumanMessage(content="second", id="u2")]}, config
    )
    other = graph.invoke(
        {"messages": [HumanMessage(content="other", id="v1")]},
        {"configurable": {"thread_id": "other"}},
    )
    assert [m.id for m in second["messages"]] == ["u1", "u2"]
    assert [m.id for m in other["messages"]] == ["v1"]
    return {"same_thread_ids": ["u1", "u2"], "other_thread_ids": ["v1"]}


def interrupted_node_restarts():
    class State(TypedDict):
        approved: bool

    effects = []

    def approval(state):
        effects.append("before_interrupt")
        decision = interrupt("approve?")
        return {"approved": decision}

    graph = chain(State, approval, saver=InMemorySaver())
    config = {"configurable": {"thread_id": "approval"}}
    first = graph.invoke({"approved": False}, config)
    assert first["__interrupt__"]
    result = graph.invoke(Command(resume=True), config)
    assert result["approved"] is True
    assert effects == ["before_interrupt", "before_interrupt"]
    return {"before_interrupt_executions": len(effects), "approved": True}


def retry_reexecutes_effect():
    class State(TypedDict):
        done: bool

    effects = []

    def flaky(state):
        effects.append("external_effect")
        if len(effects) == 1:
            raise RuntimeError("transient failure after effect")
        return {"done": True}

    graph = chain(
        State,
        flaky,
        retry=RetryPolicy(
            max_attempts=2, initial_interval=0, jitter=False, retry_on=RuntimeError
        ),
    )
    assert graph.invoke({"done": False})["done"] is True
    assert len(effects) == 2
    return {"effect_executions": len(effects), "done": True}


def pending_writes_recovery():
    class State(TypedDict):
        results: Annotated[list[str], add]

    counts = {"a": 0, "b": 0}

    def a(state):
        counts["a"] += 1
        return {"results": ["a"]}

    def b(state):
        counts["b"] += 1
        if counts["b"] == 1:
            # Let the sibling finish so its write can be recorded.
            time.sleep(0.1)
            raise RuntimeError("b fails after a succeeds")
        return {"results": ["b"]}

    builder = StateGraph(State)
    builder.add_node("a", a)
    builder.add_node("b", b)
    for name in ("a", "b"):
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "pending"}}
    try:
        graph.invoke({"results": []}, config, durability="sync")
    except RuntimeError as exc:
        assert "b fails" in str(exc)
    else:
        raise AssertionError("Expected the first execution to fail")
    result = graph.invoke(None, config, durability="sync")
    assert counts == {"a": 1, "b": 2}
    assert result["results"] == ["a", "b"]
    return {"executions": counts, "results": result["results"]}


def deepagents_message_channel():
    from deepagents.graph import DeepAgentState
    from langgraph.channels.delta import DeltaChannel

    graph = chain(DeepAgentState, lambda state: {}, saver=InMemorySaver())
    channel = graph.channels["messages"]
    assert isinstance(channel, DeltaChannel)
    assert channel.snapshot_frequency == 50
    config = {"configurable": {"thread_id": "delta-stm"}}
    graph.invoke({"messages": [HumanMessage(content="first", id="d1")]}, config)
    graph.invoke({"messages": [HumanMessage(content="second", id="d2")]}, config)
    values = graph.get_state(config).values
    assert [m.id for m in values["messages"]] == ["d1", "d2"]
    return {"channel": type(channel).__name__, "snapshot_frequency": 50,
            "restored_ids": ["d1", "d2"]}


def main():
    versions = {
        name: version(name)
        for name in (
            "deepagents", "langchain", "langchain-core", "langgraph",
            "langgraph-checkpoint", "langgraph-prebuilt",
        )
    }
    probes = (
        compiled_channels, partial_updates, step_visibility_and_aliases,
        concurrent_collision, short_term_memory, interrupted_node_restarts,
        retry_reexecutes_effect, pending_writes_recovery,
        deepagents_message_channel,
    )
    results = {}
    for probe in probes:
        results[probe.__name__] = probe()
    print(json.dumps({"versions": versions, "passed": len(results),
                      "probes": results}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
