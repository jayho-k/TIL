"""Offline examples of node updates, channel reducers and step boundaries."""

import json
from importlib.metadata import version
from operator import add
from threading import Event
from typing import Annotated, Literal

from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, Overwrite
from typing_extensions import TypedDict


class State(TypedDict):
    question: str
    results: Annotated[list[str], add]
    answer: str


def single(action, initial):
    builder = StateGraph(State)
    builder.add_node("action", action)
    builder.add_edge(START, "action")
    builder.add_edge("action", END)
    return builder.compile().invoke(initial)


def probe_partial():
    initial = {"question": "q", "results": ["seed"]}
    partial = single(lambda state: {"results": ["new"]}, initial)
    full = single(lambda state: {**state, "results": state["results"] + ["new"]}, initial)
    empty = single(lambda state: {"results": []}, initial)
    overwrite = single(lambda state: {"results": Overwrite([])}, initial)
    assert partial["results"] == ["seed", "new"]
    assert full["results"] == ["seed", "seed", "new"]
    assert empty["results"] == ["seed"]
    assert overwrite["results"] == []
    return {"partial": partial, "full": full, "empty_list": empty, "overwrite": overwrite}


def probe_return_contract():
    records = []
    builder = StateGraph(State)
    builder.add_node("noop", lambda state: None)

    def next_node(state):
        records.append("next")
        return {"anser": "typo", "answer": "ok"}

    builder.add_node("next", next_node)
    builder.add_edge(START, "noop")
    builder.add_edge("noop", "next")
    builder.add_edge("next", END)
    output = builder.compile().invoke({"question": "q"})
    assert records == ["next"]
    assert output["answer"] == "ok" and "anser" not in output
    try:
        single(lambda state: "invalid", {"question": "q"})
    except InvalidUpdateError as error:
        invalid = str(error)
    else:
        raise AssertionError("String return must fail the dict-state contract")
    return {"none_does_not_stop_edges": records, "unknown_key_filtered": output,
            "invalid_return": invalid}


def probe_parallel():
    completed = []
    inputs = []
    released = Event()

    def slow(state: State):
        inputs.append({"node": "slow", "results": list(state["results"])})
        if not released.wait(5):
            raise AssertionError("Parallel peer was not scheduled")
        completed.append("slow")
        return {"results": ["slow"]}

    def fast(state: State):
        inputs.append({"node": "fast", "results": list(state["results"])})
        completed.append("fast")
        released.set()
        return {"results": ["fast"]}

    builder = StateGraph(State)
    builder.add_node("a_slow", slow)
    builder.add_node("z_fast", fast)
    builder.add_edge(START, "a_slow")
    builder.add_edge(START, "z_fast")
    builder.add_edge("a_slow", END)
    builder.add_edge("z_fast", END)
    output = builder.compile().invoke({"question": "q", "results": ["seed"]})
    assert completed == ["fast", "slow"]
    assert all(value["results"] == ["seed"] for value in inputs)
    assert output["results"] == ["seed", "slow", "fast"]
    return {"inputs": sorted(inputs, key=lambda x: x["node"]),
            "completion_order": completed, "merged_results": output["results"]}


def probe_collision():
    builder = StateGraph(State)
    for name in ["a", "b"]:
        builder.add_node(name, lambda state: {"answer": "same"})
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    try:
        builder.compile().invoke({"question": "q"})
    except InvalidUpdateError as error:
        return {"same_value_still_conflicts": str(error)}
    raise AssertionError("Two LastValue writes must conflict even when equal")


def probe_aliases():
    class NestedState(TypedDict):
        nested: dict[str, int]

    seen = []

    def read(state: NestedState):
        seen.append((state, state["nested"]))
        return {}

    builder = StateGraph(NestedState)
    for name in ["a", "b"]:
        builder.add_node(name, read)
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    builder.compile().invoke({"nested": {"count": 0}})
    assert seen[0][0] is not seen[1][0]
    assert seen[0][1] is seen[1][1]
    return {"top_dict_is_distinct": True, "nested_object_is_shared": True}


def probe_command():
    class RouteState(TypedDict):
        value: int
        fixed_seen: bool
        chosen_seen: bool

    def source(state: RouteState) -> Command[Literal["chosen"]]:
        return Command(update={"value": 1}, goto="chosen")

    builder = StateGraph(RouteState)
    builder.add_node("source", source)
    builder.add_node("fixed", lambda state: {"fixed_seen": state["value"] == 1})
    builder.add_node("chosen", lambda state: {"chosen_seen": state["value"] == 1})
    builder.add_edge(START, "source")
    builder.add_edge("source", "fixed")
    builder.add_edge("fixed", END)
    builder.add_edge("chosen", END)
    output = builder.compile().invoke({"value": 0})
    assert output == {"value": 1, "fixed_seen": True, "chosen_seen": True}
    return output


def main():
    probes = {"partial_and_overwrite": probe_partial, "return_contract": probe_return_contract,
              "parallel_step": probe_parallel, "equal_writes_collision": probe_collision,
              "input_aliases": probe_aliases, "command_and_static_edge": probe_command}
    results = {name: {"status": "passed", "observed": probe()} for name, probe in probes.items()}
    print(json.dumps({"langgraph_version": version("langgraph"), "results": results},
                     indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
