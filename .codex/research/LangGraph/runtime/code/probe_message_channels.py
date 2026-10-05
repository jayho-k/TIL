"""Observe message identity, DeepAgentState delta writes and restoration."""

import json
from importlib.metadata import version

from deepagents._messages_reducer import _messages_delta_reducer
from deepagents.graph import DeepAgentState
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langgraph.channels.delta import DeltaChannel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import REMOVE_ALL_MESSAGES, add_messages


def simplified(messages):
    return [{"id": m.id, "type": m.type, "content": m.content} for m in messages]


def probe_identity():
    original = [HumanMessage(content="old", id="u1"), AIMessage(content="first", id="a1")]
    updated = add_messages(original, [HumanMessage(content="edited", id="u1")])
    assert [m.id for m in updated] == ["u1", "a1"]
    assert updated[0].content == "edited"
    appended = add_messages(updated, [HumanMessage(content="new", id="u2")])
    assert len(appended) == 3
    removed = add_messages(appended, [RemoveMessage(id="a1")])
    assert [m.id for m in removed] == ["u1", "u2"]
    reset = add_messages(removed, [RemoveMessage(id=REMOVE_ALL_MESSAGES), HumanMessage(content="reset", id="r1")])
    assert [m.id for m in reset] == ["r1"]
    return {"replaced": simplified(updated), "removed": simplified(removed), "reset": simplified(reset)}


def probe_difference():
    try:
        add_messages([], [RemoveMessage(id="missing")])
    except ValueError as error:
        standard_error = str(error)
    else:
        raise AssertionError("Standard reducer must reject unknown deletion")
    delta_result = _messages_delta_reducer([], [[RemoveMessage(id="missing")]])
    assert delta_result == []
    without_id = HumanMessage(content="no id")
    direct = _messages_delta_reducer([], [[without_id]])
    assert direct[0].id is None
    standard = add_messages([], [HumanMessage(content="no id")])
    assert standard[0].id is not None
    return {"standard_unknown_delete": standard_error, "deepagent_unknown_delete": [],
            "deepagent_direct_reducer_assigns_id": False, "standard_assigns_id": True}


def probe_batches():
    xs = [[HumanMessage(content="one", id="u1")], [HumanMessage(content="edited", id="u1")]]
    ys = [[AIMessage(content="reply", id="a1")], [RemoveMessage(id="u1")]]
    grouped = _messages_delta_reducer(_messages_delta_reducer([], xs), ys)
    combined = _messages_delta_reducer([], xs + ys)
    assert simplified(grouped) == simplified(combined)
    return {"grouped": simplified(grouped), "combined": simplified(combined)}


def probe_update_and_replay():
    calls = []

    def batch_sum(state, writes):
        calls.append({"base": list(state), "writes": [list(w) for w in writes]})
        return list(state) + [value for write in writes for value in write]

    channel = DeltaChannel(batch_sum, typ=list, snapshot_frequency=2)
    channel.update([[1]])
    assert channel.get() == [1]
    channel.replay_writes([("task", "items", [2])])
    assert channel.get() == [1, 2]
    assert len(calls) == 2
    return {"reducer_calls": calls, "value": channel.get()}


def probe_graph_restore():
    saver = InMemorySaver()

    def reply(state: DeepAgentState):
        humans = [m for m in state["messages"] if isinstance(m, HumanMessage)]
        return {"messages": [AIMessage(content="reply " + str(len(humans)))]}

    builder = StateGraph(DeepAgentState)
    builder.add_node("reply", reply)
    builder.add_edge(START, "reply")
    builder.add_edge("reply", END)
    graph = builder.compile(checkpointer=saver)
    config = {"configurable": {"thread_id": "message-probe"}}
    graph.invoke({"messages": [HumanMessage(content="one")]}, config, durability="sync")
    graph.invoke({"messages": [HumanMessage(content="two")]}, config, durability="sync")
    first = graph.get_state(config)
    second = graph.get_state(config)
    assert [m.content for m in first.values["messages"]] == ["one", "reply 1", "two", "reply 2"]
    ids = [m.id for m in first.values["messages"]]
    assert all(ids) and len(set(ids)) == 4
    assert ids == [m.id for m in second.values["messages"]]
    stored = saver.get_tuple(config)
    assert stored is not None
    assert "messages" not in stored.checkpoint["channel_values"]
    spec = graph.channels["messages"]
    assert isinstance(spec, DeltaChannel) and spec.snapshot_frequency == 50
    history = saver.get_delta_channel_history(config=stored.config, channels=["messages"])
    assert history["messages"]["writes"]
    return {"channel": type(spec).__name__, "snapshot_frequency": spec.snapshot_frequency,
            "latest_checkpoint_contains_full_messages": False,
            "restored_contents": [m.content for m in first.values["messages"]],
            "stable_ids_across_reads": True,
            "ancestor_message_writes": len(history["messages"]["writes"]),
            "next_nodes": list(first.next)}


def main():
    probes = {"message_identity": probe_identity, "reducer_differences": probe_difference,
              "batch_example": probe_batches, "update_and_replay": probe_update_and_replay,
              "deepagent_restore": probe_graph_restore}
    results = {name: {"status": "passed", "observed": probe()} for name, probe in probes.items()}
    print(json.dumps({"langgraph_version": version("langgraph"), "deepagents_version": version("deepagents"),
                      "results": results}, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
