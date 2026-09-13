from app.domain.models import RunStatus


def inspect_checkpoint(snapshot):
    """Find nested review interrupts and the file agent's durable state."""
    interrupts = {}
    states = []

    def visit(current):
        values = getattr(current, "values", {})
        if isinstance(values, dict) and "phase" in values:
            states.append(values)
        for item in getattr(current, "interrupts", ()):
            interrupts[item.id] = item
        for task in getattr(current, "tasks", ()):
            for item in task.interrupts:
                interrupts[item.id] = item
            if hasattr(task.state, "values"):
                visit(task.state)

    visit(snapshot)
    return list(interrupts.values()), states[-1] if states else {}


BUSY_STATUSES = {
    RunStatus.RUNNING,
    RunStatus.RESUMING,
    RunStatus.FAILED,
    RunStatus.RECOVERY_REQUIRED,
}


def file_snapshot(snapshot):
    if "phase" in getattr(snapshot, "values", {}):
        return snapshot
    for task in getattr(snapshot, "tasks", ()):
        if hasattr(task.state, "values"):
            found = file_snapshot(task.state)
            if found:
                return found
    return None


async def load_file_snapshot(agent, root, record):
    """Adapter for tool-invoked subgraphs, which root.get_state cannot discover.

    Namespace/checkpointer routing follows the pinned LangGraph implementation.
    Keep this isolated and covered by real nested resume tests on upgrades.
    """
    from langgraph._internal._constants import CONFIG_KEY_CHECKPOINTER

    graph = agent.file_translation_graph
    for task in root.tasks:
        if task.name != "tools":
            continue
        config = {
            "configurable": {
                "thread_id": record.thread_id,
                "checkpoint_ns": f"tools:{task.id}",
                CONFIG_KEY_CHECKPOINTER: agent.checkpointer,
            }
        }
        child = await graph.aget_state(config)
        if child.values.get("run_id") == record.run_id:
            return graph, child, config
    return graph, None, None
