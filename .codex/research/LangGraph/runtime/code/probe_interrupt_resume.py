"""Observe dynamic interrupts, ordered resumes, mappings and static breakpoints."""

import json
from importlib.metadata import version

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict


def compile_single(schema, action, *, interrupt_before=None):
    builder = StateGraph(schema)
    builder.add_node("review", action)
    builder.add_edge(START, "review")
    builder.add_edge("review", END)
    return builder.compile(checkpointer=InMemorySaver(), interrupt_before=interrupt_before)


def probe_single():
    class State(TypedDict):
        approved: bool

    calls = {"before": 0, "after": 0}

    def review(state: State):
        calls["before"] += 1
        approval = interrupt({"question": "approve?"})
        calls["after"] += 1
        return {"approved": approval}

    graph = compile_single(State, review)
    config = {"configurable": {"thread_id": "approval"}}
    paused = graph.invoke({}, config, durability="sync")
    snapshot = graph.get_state(config)
    assert len(paused["__interrupt__"]) == 1 and snapshot.next == ("review",)
    assert calls == {"before": 1, "after": 0}
    final = graph.invoke(Command(resume=False), config, durability="sync")
    assert final["approved"] is False
    assert calls == {"before": 2, "after": 1}
    assert graph.get_state(config).interrupts == ()
    return {"paused_next": list(snapshot.next), "paused_payload": snapshot.interrupts[0].value,
            "calls_after_resume": calls, "final": final}


def probe_multiple_in_node():
    class State(TypedDict):
        name: str
        age: int

    calls = {"before_first": 0, "between": 0}

    def review(state: State):
        calls["before_first"] += 1
        name = interrupt("name?")
        calls["between"] += 1
        age = interrupt("age?")
        return {"name": name, "age": age}

    graph = compile_single(State, review)
    config = {"configurable": {"thread_id": "two-questions"}}
    first = graph.invoke({}, config, durability="sync")
    assert first["__interrupt__"][0].value == "name?"
    second = graph.invoke(Command(resume="Jay"), config, durability="sync")
    assert second["__interrupt__"][0].value == "age?"
    final = graph.invoke(Command(resume=30), config, durability="sync")
    assert final == {"name": "Jay", "age": 30}
    assert calls == {"before_first": 3, "between": 2}
    return {"first_question": "name?", "second_question": "age?", "calls": calls, "final": final}


def probe_none_is_not_answer():
    class State(TypedDict):
        answer: str

    calls = []

    def review(state: State):
        calls.append("entered")
        return {"answer": interrupt("answer?")}

    graph = compile_single(State, review)
    config = {"configurable": {"thread_id": "no-answer"}}
    graph.invoke({}, config, durability="sync")
    repeated = graph.invoke(None, config, durability="sync")
    assert len(repeated["__interrupt__"]) == 1 and len(calls) == 2
    return {"none_input_reinterrupts": True, "entry_count": len(calls)}


def probe_parallel_map():
    class State(TypedDict):
        a: str
        b: str

    def node_a(state: State):
        return {"a": interrupt("a")}

    def node_b(state: State):
        return {"b": interrupt("b")}

    builder = StateGraph(State)
    for name, action in [("a", node_a), ("b", node_b)]:
        builder.add_node(name, action)
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "parallel"}}
    paused = graph.invoke({}, config, durability="sync")
    interruptions = paused["__interrupt__"]
    assert len(interruptions) == 2
    try:
        graph.invoke(Command(resume="scalar"), config, durability="sync")
    except RuntimeError as error:
        scalar_error = str(error)
        assert "multiple pending interrupts" in scalar_error
    else:
        raise AssertionError("Multiple pending interrupts require ID mapping")
    replies = {item.id: "ok-" + item.value for item in interruptions}
    final = graph.invoke(Command(resume=replies), config, durability="sync")
    assert final == {"a": "ok-a", "b": "ok-b"}
    return {"pending_interrupts": len(interruptions), "scalar_resume_error": scalar_error,
            "mapping_resolves_both": True, "final": final}


def probe_static():
    class State(TypedDict):
        done: bool

    calls = []

    def review(state: State):
        calls.append("review")
        return {"done": True}

    graph = compile_single(State, review, interrupt_before=["review"])
    config = {"configurable": {"thread_id": "static"}}
    graph.invoke({}, config, durability="sync")
    snapshot = graph.get_state(config)
    assert calls == [] and snapshot.next == ("review",)
    final = graph.invoke(None, config, durability="sync")
    assert final["done"] is True and calls == ["review"]
    return {"node_called_before_pause": False, "none_continues_static_pause": True, "final": final}


def main():
    probes = {"single_approval": probe_single, "ordered_interrupts": probe_multiple_in_node,
              "none_is_not_answer": probe_none_is_not_answer, "parallel_resume_map": probe_parallel_map,
              "static_breakpoint": probe_static}
    results = {name: {"status": "passed", "observed": probe()} for name, probe in probes.items()}
    print(json.dumps({"langgraph_version": version("langgraph"), "results": results}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
