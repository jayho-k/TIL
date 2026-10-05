"""Observe reducers, routing and node attribution in update_state."""

import json
from importlib.metadata import version
from operator import add
from typing import Annotated, Literal

from deepagents.graph import DeepAgentState
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Overwrite
from typing_extensions import TypedDict


class State(TypedDict):
    results: Annotated[list[str], add]
    answer: str


def make_graph():
    calls = []

    def search(state: State):
        calls.append("search")
        return {"results": ["seed"]}

    def route(state: State) -> Literal["answer", "__end__"]:
        calls.append("route")
        return "answer" if state["results"] else END

    def answer(state: State):
        calls.append("answer")
        return {"answer": " | ".join(state["results"])}

    builder = StateGraph(State)
    builder.add_node("search", search)
    builder.add_node("answer", answer)
    builder.add_edge(START, "search")
    builder.add_conditional_edges("search", route)
    builder.add_edge("answer", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "edit"}}
    graph.invoke({"results": []}, config, durability="sync")
    return graph, config, calls


def probe_writer_routing():
    graph, config, calls = make_graph()
    previous = graph.get_state(config)
    calls_before = len(calls)
    updated = graph.update_state(config, {"results": ["manual"]}, as_node="search")
    after = graph.get_state(updated)
    assert calls[calls_before:] == ["route"]
    assert after.values["results"] == ["seed", "manual"]
    assert after.next == ("answer",)
    assert after.values["answer"] == "seed"
    assert after.metadata["source"] == "update"
    assert updated["configurable"]["checkpoint_id"] != previous.config["configurable"]["checkpoint_id"]
    historical = graph.get_state(previous.config)
    assert historical.values["results"] == ["seed"]
    final = graph.invoke(None, updated, durability="sync")
    assert final["answer"] == "seed | manual"
    assert calls[calls_before:] == ["route", "answer"]
    return {"calls_during_update": ["route"], "after_update_values": after.values,
            "after_update_next": list(after.next), "source": after.metadata["source"],
            "new_checkpoint_created": True, "old_checkpoint_values": historical.values,
            "after_continue": final}


def probe_attribution_and_reset():
    graph, config, calls = make_graph()
    before = len(calls)
    updated = graph.update_state(config, {"results": ["manual"]}, as_node="answer")
    after = graph.get_state(updated)
    assert calls[before:] == []
    assert after.next == () and after.values["results"] == ["seed", "manual"]
    assert after.values["answer"] == "seed"
    reset = graph.update_state(updated, {"results": Overwrite([])}, as_node="search")
    reset_state = graph.get_state(reset)
    assert calls[before:] == ["route"]
    assert reset_state.values["results"] == [] and reset_state.next == ()
    return {"as_answer_next": list(after.next), "as_answer_values": after.values,
            "reset_values": reset_state.values, "reset_next": list(reset_state.next)}


def probe_ambiguous():
    builder = StateGraph(State)
    for name in ["a", "b"]:
        builder.add_node(name, lambda state: {"results": ["value"]})
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "ambiguous"}}
    graph.invoke({"results": []}, config, durability="sync")
    try:
        graph.update_state(config, {"results": ["manual"]})
    except InvalidUpdateError as error:
        assert "Ambiguous" in str(error)
        return {"error": str(error)}
    raise AssertionError("Parallel last writers must require explicit attribution")


def probe_message_ids():
    builder = StateGraph(DeepAgentState)
    builder.add_node("noop", lambda state: {})
    builder.add_edge(START, "noop")
    builder.add_edge("noop", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "manual-messages"}}
    graph.invoke({"messages": [HumanMessage(content="first", id="u1")]}, config, durability="sync")
    no_id = graph.update_state(config, {"messages": [HumanMessage(content="manual")]}, as_node="noop")
    no_id_state = graph.get_state(no_id)
    assert no_id_state.values["messages"][-1].id is None
    explicit = graph.update_state(no_id, {"messages": [HumanMessage(content="explicit", id="manual-id")]}, as_node="noop")
    first = graph.get_state(explicit)
    second = graph.get_state(explicit)
    assert first.values["messages"][-1].id == second.values["messages"][-1].id == "manual-id"
    return {"update_state_auto_assigns_missing_id_in_this_case": False,
            "explicit_id_preserved_across_reads": True,
            "contents": [m.content for m in first.values["messages"]]}


def main():
    probes = {"writers_and_routing": probe_writer_routing, "attribution_and_overwrite": probe_attribution_and_reset,
              "ambiguous_attribution": probe_ambiguous, "deepagent_manual_message_ids": probe_message_ids}
    results = {name: {"status": "passed", "observed": probe()} for name, probe in probes.items()}
    print(json.dumps({"langgraph_version": version("langgraph"), "results": results}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
