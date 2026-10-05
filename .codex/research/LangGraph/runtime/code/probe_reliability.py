"""Observe retry scope, async node timeout and durability ordering offline."""

import asyncio
import json
from importlib.metadata import version
from operator import add
from typing import Annotated

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import NodeTimeoutError
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy
from typing_extensions import TypedDict


class State(TypedDict):
    value: int
    records: Annotated[list[str], add]


def build(action, **kwargs):
    builder = StateGraph(State)
    builder.add_node("work", action, **kwargs)
    builder.add_edge(START, "work")
    builder.add_edge("work", END)
    return builder.compile()


def probe_retry():
    effects = []

    def work(state: State):
        effects.append("external-change")
        if len(effects) < 3:
            raise ValueError("temporary")
        return {"records": ["success"]}

    policy = RetryPolicy(max_attempts=3, initial_interval=0, jitter=False, retry_on=ValueError)
    output = build(work, retry_policy=policy).invoke({"value": 0})
    assert len(effects) == 3 and output["records"] == ["success"]
    attempts = []

    def nonmatching(state: State):
        attempts.append(1)
        raise TypeError("not matching")

    try:
        build(nonmatching, retry_policy=policy).invoke({"value": 0})
    except TypeError:
        pass
    else:
        raise AssertionError("Unmatched error must propagate")
    assert len(attempts) == 1
    return {"external_effect_count": len(effects), "channel_results": output["records"],
            "unmatched_error_attempts": len(attempts)}


async def probe_timeout():
    effects = []
    cancelled = asyncio.Event()

    async def work(state: State):
        effects.append("external-change")
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            raise

    graph = build(work, timeout=0.02)
    try:
        await graph.ainvoke({"value": 0})
    except NodeTimeoutError as error:
        kind = error.kind
    else:
        raise AssertionError("Async node must time out")
    await asyncio.wait_for(cancelled.wait(), 2)
    assert kind == "run" and effects == ["external-change"]
    try:
        build(lambda state: {}, timeout=0.02)
    except ValueError as error:
        sync_error = str(error)
        assert "only supported for async nodes" in sync_error
    else:
        raise AssertionError("Sync node timeout must be rejected")
    return {"timeout_kind": kind, "node_cancellation_observed": True,
            "external_effect_remains": True, "sync_timeout_error": sync_error}


async def probe_durability(mode):
    saving_first = asyncio.Event()
    release_save = asyncio.Event()
    first_saved = asyncio.Event()
    second_started = asyncio.Event()
    saved_values = []
    seen = []

    class ControlledSaver(InMemorySaver):
        async def aput(self, config, checkpoint, metadata, new_versions):
            value = checkpoint["channel_values"].get("value")
            if metadata.get("source") == "loop" and value == 1:
                saving_first.set()
                await release_save.wait()
                result = await super().aput(config, checkpoint, metadata, new_versions)
                saved_values.append(value)
                first_saved.set()
                return result
            result = await super().aput(config, checkpoint, metadata, new_versions)
            saved_values.append(value)
            return result

    async def first(state: State):
        return {"value": 1}

    async def second(state: State):
        seen.append(first_saved.is_set())
        second_started.set()
        return {"value": 2}

    saver = ControlledSaver()
    builder = StateGraph(State)
    builder.add_node("first", first)
    builder.add_node("second", second)
    builder.add_edge(START, "first")
    builder.add_edge("first", "second")
    builder.add_edge("second", END)
    graph = builder.compile(checkpointer=saver)
    config = {"configurable": {"thread_id": mode}}
    run = asyncio.create_task(graph.ainvoke({"value": 0}, config, durability=mode))
    if mode != "exit":
        await asyncio.wait_for(saving_first.wait(), 3)
        if mode == "async":
            await asyncio.wait_for(second_started.wait(), 3)
        else:
            assert not second_started.is_set()
        release_save.set()
    output = await asyncio.wait_for(run, 3)
    assert output["value"] == 2
    assert seen == [mode == "sync"]
    if mode == "exit":
        assert 1 not in saved_values
    assert graph.get_state(config).values["value"] == 2
    return {"second_started_after_first_save": seen[0], "saved_values": saved_values,
            "final_value": output["value"]}


async def async_probes():
    return {"node_timeout": await probe_timeout(),
            **{f"durability_{mode}": await probe_durability(mode) for mode in ["sync", "async", "exit"]}}


def main():
    observations = {"retry_scope": probe_retry(), **asyncio.run(async_probes())}
    print(json.dumps({"langgraph_version": version("langgraph"),
                      "results": {name: {"status": "passed", "observed": value}
                                  for name, value in observations.items()}}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
