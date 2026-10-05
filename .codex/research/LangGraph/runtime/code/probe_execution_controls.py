"""Observe context, cache keys, per-run concurrency and recursion limits."""

import asyncio
import json
from dataclasses import dataclass
from importlib.metadata import version
from operator import add
from typing import Annotated

from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.types import CachePolicy
from typing_extensions import TypedDict


class State(TypedDict):
    question: str
    response: str


@dataclass
class Context:
    tenant: str
    client: object = None


def make_context_graph(*, cache=None, saver=None, calls=None):
    def work(state: State, runtime: Runtime[Context]):
        if calls is not None:
            calls.append(runtime.context.tenant)
        return {"response": runtime.context.tenant + ":" + state["question"]}

    builder = StateGraph(State, context_schema=Context)
    builder.add_node("work", work, cache_policy=CachePolicy() if cache else None)
    builder.add_edge(START, "work")
    builder.add_edge("work", END)
    return builder.compile(cache=cache, checkpointer=saver)


def probe_context():
    graph = make_context_graph(saver=InMemorySaver())
    config = {"configurable": {"thread_id": "context"}}
    client = object()
    output = graph.invoke({"question": "q"}, config, context=Context("A", client), durability="sync")
    assert output["response"] == "A:q"
    snapshot = graph.get_state(config)
    assert set(snapshot.values) == {"question", "response"}
    converted = graph.invoke({"question": "q"}, config, context={"tenant": "B"}, durability="sync")
    assert converted["response"] == "B:q"
    return {"runtime_context_used": True, "saved_keys": sorted(snapshot.values),
            "client_stored_in_state": False, "dict_context_coerced": converted["response"]}


def probe_cache_context():
    calls = []
    graph = make_context_graph(cache=InMemoryCache(), calls=calls)
    a = graph.invoke({"question": "q"}, context=Context("A"))
    b = graph.invoke({"question": "q"}, context=Context("B"))
    assert a["response"] == b["response"] == "A:q" and calls == ["A"]
    graph.clear_cache(["work"])
    after_clear = graph.invoke({"question": "q"}, context=Context("B"))
    assert after_clear["response"] == "B:q" and calls == ["A", "B"]

    class TenantState(State):
        tenant: str

    fixed_calls = []

    def fixed(state: TenantState, runtime: Runtime[Context]):
        assert state["tenant"] == runtime.context.tenant
        fixed_calls.append(state["tenant"])
        return {"response": runtime.context.tenant + ":" + state["question"]}

    builder = StateGraph(TenantState, context_schema=Context)
    builder.add_node("work", fixed, cache_policy=CachePolicy())
    builder.add_edge(START, "work")
    builder.add_edge("work", END)
    fixed_graph = builder.compile(cache=InMemoryCache())
    fixed_a = fixed_graph.invoke({"question": "q", "tenant": "A"}, context=Context("A"))
    fixed_b = fixed_graph.invoke({"question": "q", "tenant": "B"}, context=Context("B"))
    assert fixed_a["response"] == "A:q" and fixed_b["response"] == "B:q"
    assert fixed_calls == ["A", "B"]
    return {"context_only_cache_result": b["response"], "context_only_calls": ["A"],
            "after_clear_result": after_clear["response"],
            "tenant_in_node_input_results": [fixed_a["response"], fixed_b["response"]]}


async def probe_concurrency():
    class FanState(TypedDict):
        records: Annotated[list[str], add]

    active = 0
    peak = 0
    calls = []

    def node(name):
        async def work(state: FanState):
            nonlocal active, peak
            active += 1
            peak = max(peak, active)
            calls.append(name)
            await asyncio.sleep(0.02)
            active -= 1
            return {"records": [name]}
        return work

    builder = StateGraph(FanState)
    for index in range(5):
        name = "node" + str(index)
        builder.add_node(name, node(name))
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    output = await builder.compile().ainvoke({}, {"max_concurrency": 2, "recursion_limit": 3})
    assert peak == 2 and len(calls) == 5 and len(output["records"]) == 5
    return {"configured_max_concurrency": 2, "peak_node_concurrency": peak,
            "node_calls": len(calls), "recursion_limit": 3}


async def probe_same_thread():
    class ThreadState(TypedDict):
        value: int
        response: int

    both_entered = asyncio.Event()
    release = asyncio.Event()
    entered = []

    async def work(state: ThreadState):
        entered.append(state["value"])
        if len(entered) == 2:
            both_entered.set()
        await release.wait()
        return {"response": state["value"]}

    builder = StateGraph(ThreadState)
    builder.add_node("work", work)
    builder.add_edge(START, "work")
    builder.add_edge("work", END)
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "same-thread"}}
    tasks = [asyncio.create_task(graph.ainvoke({"value": n}, config, durability="sync")) for n in [1, 2]]
    try:
        await asyncio.wait_for(both_entered.wait(), 3)
    finally:
        release.set()
    results = await asyncio.wait_for(asyncio.gather(*tasks), 3)
    assert sorted(entered) == [1, 2]
    return {"both_nodes_enter_before_release": True,
            "call_outputs": sorted(result["response"] for result in results),
            "final_checkpoint_winner_asserted": False}


def probe_recursion():
    class CountState(TypedDict):
        count: int

    calls = []

    def tick(state: CountState):
        calls.append(1)
        return {"count": state["count"] + 1}

    builder = StateGraph(CountState)
    builder.add_node("tick", tick)
    builder.add_edge(START, "tick")
    builder.add_edge("tick", "tick")
    try:
        builder.compile().invoke({"count": 0}, {"recursion_limit": 3})
    except GraphRecursionError:
        pass
    else:
        raise AssertionError("Unbounded loop must fail its step limit")
    assert calls
    fixed = StateGraph(CountState)
    fixed.add_node("tick", tick)
    fixed.add_edge(START, "tick")
    fixed.add_conditional_edges("tick", lambda state: END if state["count"] >= 3 else "tick",
                                {END: END, "tick": "tick"})
    output = fixed.compile().invoke({"count": 0}, {"recursion_limit": 10})
    assert output["count"] == 3
    return {"unbounded_loop_error": "GraphRecursionError", "with_stop_condition": output}


async def async_probes():
    return {"concurrency_limit": await probe_concurrency(), "same_thread_overlap": await probe_same_thread()}


def main():
    observations = {"context_and_state": probe_context(), "cache_and_context": probe_cache_context(),
                    "recursion_limit": probe_recursion(), **asyncio.run(async_probes())}
    print(json.dumps({"langgraph_version": version("langgraph"),
                      "results": {name: {"status": "passed", "observed": value}
                                  for name, value in observations.items()}}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
