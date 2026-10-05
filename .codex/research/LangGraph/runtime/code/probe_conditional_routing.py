"""Observe registration, branch readers, routing writes and next-step execution."""

import asyncio
import json
from importlib.metadata import version
from operator import add
from typing import Annotated, Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from typing_extensions import TypedDict


class State(TypedDict):
    question: str
    results: Annotated[list[str], add]
    answer: str
    audited: bool


class RouteInput(TypedDict):
    results: Annotated[list[str], add]


def build(*, static_audit=False, invalid_label=False, narrow_router=False):
    events = []

    def record(name, state, config):
        events.append({
            "name": name,
            "step": config["metadata"]["langgraph_step"],
            "keys": sorted(state),
            "results": list(state.get("results", [])),
        })

    def search(state: State, config: RunnableConfig):
        record("search", state, config)
        return {"results": [] if state["question"] == "empty" else ["evidence"]}

    def route(state: State, config: RunnableConfig) -> Literal["found", "empty"]:
        record("route", state, config)
        if invalid_label:
            return "not_in_map"
        return "found" if state["results"] else "empty"

    def narrow_route(state: RouteInput, config: RunnableConfig) -> Literal["found", "empty"]:
        record("route", state, config)
        return "found" if state["results"] else "empty"

    def answer(state: State, config: RunnableConfig):
        record("answer", state, config)
        return {"answer": " | ".join(state["results"])}

    def audit(state: State, config: RunnableConfig):
        record("audit", state, config)
        return {"audited": True}

    builder = StateGraph(State)
    builder.add_node("search", search)
    builder.add_node("answer", answer)
    builder.add_node("audit", audit)
    builder.add_edge(START, "search")
    router = narrow_route if narrow_router else route
    builder.add_conditional_edges("search", router, {"found": "answer", "empty": END})
    if static_audit:
        builder.add_edge("search", "audit")
    builder.add_edge("answer", END)
    builder.add_edge("audit", END)
    branch = next(iter(builder.branches["search"].values()))
    registration = {
        "branch_class": type(branch).__name__,
        "path_class": type(branch.path).__name__,
        "ends": branch.ends,
        "input_schema": branch.input_schema.__name__,
        "events": list(events),
    }
    graph = builder.compile()
    assert events == []
    return builder, graph, events, registration


def probe_normal():
    builder, graph, events, registration = build()
    output = graph.invoke({"question": "runtime"})
    assert [e["name"] for e in events] == ["search", "route", "answer"]
    assert events[0]["results"] == []
    assert events[1]["results"] == ["evidence"]
    assert events[1]["step"] == events[0]["step"]
    assert events[2]["step"] == events[0]["step"] + 1
    assert output["answer"] == "evidence"
    return {
        "registration": registration,
        "search_writers": [type(w).__name__ for w in graph.nodes["search"].writers],
        "answer_triggers": graph.nodes["answer"].triggers,
        "events": events,
        "output": output,
    }


def probe_end():
    _, graph, events, _ = build()
    output = graph.invoke({"question": "empty"})
    assert [e["name"] for e in events] == ["search", "route"]
    assert "answer" not in output
    return {"events": events, "output": output}


def probe_static_edge():
    _, graph, events, _ = build(static_audit=True)
    output = graph.invoke({"question": "empty"})
    assert [e["name"] for e in events] == ["search", "route", "audit"]
    assert output["audited"] is True
    return {"events": events, "output": output}


def probe_narrow_reader():
    _, graph, events, registration = build(narrow_router=True)
    graph.invoke({"question": "runtime"})
    assert events[1]["keys"] == ["results"]
    return {"registration": registration, "router_input": events[1]}


def probe_errors():
    builder, graph, _, _ = build(invalid_label=True)
    try:
        graph.invoke({"question": "runtime"})
    except KeyError as error:
        invalid_label = str(error)
    else:
        raise AssertionError("Unmapped label must raise KeyError")
    branch = next(iter(builder.branches["search"].values()))
    try:
        builder.add_conditional_edges("search", branch.path, branch.ends)
    except ValueError as error:
        duplicate_branch = str(error)
    else:
        raise AssertionError("Duplicate branch name must fail")
    invalid = StateGraph(State)
    invalid.add_node("search", lambda state: {})
    invalid.add_edge(START, "search")
    invalid.add_conditional_edges("search", lambda state: "found", {"found": "missing"})
    try:
        invalid.compile()
    except ValueError as error:
        unknown_target = str(error)
    else:
        raise AssertionError("Unknown mapped target must fail validation")
    return {"unmapped_label": invalid_label, "duplicate_branch": duplicate_branch,
            "unknown_mapped_target": unknown_target}


def probe_send():
    class FanState(TypedDict):
        items: list[str]
        processed: Annotated[list[str], add]

    class WorkerInput(TypedDict):
        item: str

    received = []

    def dispatch(state: FanState):
        return [Send("worker", {"item": item}) for item in state["items"]]

    def worker(state: WorkerInput):
        received.append(dict(state))
        return {"processed": [state["item"].upper()]}

    builder = StateGraph(FanState)
    builder.add_node("worker", worker)
    builder.add_conditional_edges(START, dispatch, ["worker"])
    builder.add_edge("worker", END)
    graph = builder.compile()
    output = graph.invoke({"items": ["a", "b"]})
    assert sorted(output["processed"]) == ["A", "B"]
    assert sorted(value["item"] for value in received) == ["a", "b"]
    assert all(set(value) == {"item"} for value in received)
    return {"worker_inputs": sorted(received, key=lambda x: x["item"]), "output": output}


def probe_async():
    _, graph, events, _ = build()
    output = asyncio.run(graph.ainvoke({"question": "runtime"}))
    assert [e["name"] for e in events] == ["search", "route", "answer"]
    assert output["answer"] == "evidence"
    return {"events": events, "output": output}


def main():
    probes = {"normal_route": probe_normal, "route_to_end": probe_end,
              "static_edge_and_end": probe_static_edge, "narrow_router_input": probe_narrow_reader,
              "routing_errors": probe_errors, "send_inputs": probe_send,
              "async_route": probe_async}
    results = {name: {"status": "passed", "observed": probe()} for name, probe in probes.items()}
    print(json.dumps({"langgraph_version": version("langgraph"), "results": results},
                     indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
