"""Inspect StateGraph construction and compilation without a model or store."""

import json
from importlib.metadata import version
from operator import add
from typing import Annotated

from langgraph.channels.binop import BinaryOperatorAggregate
from langgraph.channels.last_value import LastValue
from langgraph.graph import END, START, StateGraph
from langgraph.pregel import Pregel
from typing_extensions import TypedDict


class InputState(TypedDict):
    question: str


class OutputState(TypedDict):
    answer: str


class State(InputState, OutputState):
    results: Annotated[list[str], add]


calls = []


class SearchInput(TypedDict):
    question: str


class ExtendedInput(TypedDict):
    question: str
    private_note: str


def narrow(data: SearchInput):
    return {}


def extended(data: ExtendedInput):
    return {}


def inspect_registration():
    builder = StateGraph(State)
    builder.add_node(narrow)
    builder.add_node("explicit", narrow, input_schema=State)
    builder.add_node(extended)
    assert builder.nodes["narrow"].input_schema is SearchInput
    assert builder.nodes["explicit"].input_schema is State
    assert "private_note" in builder.channels
    builder.add_edge("not_registered", "also_missing")
    builder.add_edge("not_registered", "also_missing")
    assert len(builder.edges) == 1
    builder.add_edge(START, "narrow")
    try:
        builder.compile()
    except ValueError as error:
        compile_error = str(error)
    else:
        raise AssertionError("Unknown string edge must fail validation")
    try:
        builder.add_edge(["not_registered"], "narrow")
    except ValueError as error:
        list_edge_error = str(error)
    else:
        raise AssertionError("Unknown list source must fail registration")
    assert calls == []
    return {
        "inferred_name": "narrow",
        "inferred_input_schema": builder.nodes["narrow"].input_schema.__name__,
        "explicit_input_schema": builder.nodes["explicit"].input_schema.__name__,
        "added_channel": "private_note",
        "duplicate_string_edge_stored_once": True,
        "string_edge_compile_error": compile_error,
        "list_edge_registration_error": list_edge_error,
    }


def search(state: State):
    calls.append("search")
    return {"results": ["evidence for " + state["question"]]}


def answer(state: State):
    calls.append("answer")
    return {"answer": " | ".join(state["results"])}


def main():
    builder = StateGraph(State, input_schema=InputState, output_schema=OutputState)
    assert isinstance(builder.channels["question"], LastValue)
    assert isinstance(builder.channels["answer"], LastValue)
    assert isinstance(builder.channels["results"], BinaryOperatorAggregate)
    before_compile = {
        "channels": {k: type(v).__name__ for k, v in builder.channels.items()},
        "nodes": list(builder.nodes),
        "calls": list(calls),
    }
    builder.add_node("search", search)
    builder.add_node("answer", answer)
    after_add_node = {
        name: {
            "class": type(spec).__name__,
            "runnable": type(spec.runnable).__name__,
            "input_schema": spec.input_schema.__name__,
            "has_triggers": hasattr(spec, "triggers"),
            "has_writers": hasattr(spec, "writers"),
        }
        for name, spec in builder.nodes.items()
    }
    builder.add_edge(START, "search")
    builder.add_edge("search", "answer")
    builder.add_edge("answer", END)
    after_add_edge = {
        "edges": sorted(builder.edges),
        "waiting_edges": list(builder.waiting_edges),
        "calls": list(calls),
    }
    assert calls == []
    registration_checks = inspect_registration()
    graph = builder.compile()
    assert calls == []
    assert isinstance(graph, Pregel)
    assert graph.input_channels == START
    assert graph.output_channels == ["answer"]
    assert set(graph.stream_channels) == {"question", "answer", "results"}
    assert graph.nodes["search"].triggers == ["branch:to:search"]
    assert graph.nodes["answer"].triggers == ["branch:to:answer"]
    after_compile = {
        "class": type(graph).__name__,
        "base_is_pregel": True,
        "channels": {k: type(v).__name__ for k, v in graph.channels.items()},
        "input_channels": graph.input_channels,
        "output_channels": graph.output_channels,
        "stream_channels": graph.stream_channels,
        "nodes": {
            name: {
                "class": type(node).__name__,
                "channels": node.channels,
                "triggers": node.triggers,
                "writers": [type(writer).__name__ for writer in node.writers],
            }
            for name, node in graph.nodes.items()
        },
        "calls": list(calls),
    }
    result = graph.invoke({"question": "runtime"})
    assert result == {"answer": "evidence for runtime"}
    assert calls == ["search", "answer"]
    report = {
        "langgraph_version": version("langgraph"),
        "before_compile": before_compile,
        "after_add_node": after_add_node,
        "after_add_edge": after_add_edge,
        "registration_checks": registration_checks,
        "after_compile": after_compile,
        "after_invoke": {"calls": calls, "output": result},
    }
    print(json.dumps(report, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
