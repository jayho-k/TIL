import sys

from langgraph.checkpoint.memory import MemorySaver, InMemorySaver

from graph import build_graph

thread = sys.argv[1] if len(sys.argv) > 1 else "trip-3"
graph = build_graph(checkpointer=MemorySaver())
snapshot = graph.get_state({"configurable": {"thread_id": thread}})

if snapshot.values:
    print("찾음:", snapshot.values["total"])
else:
    print("저장된 상태 없음")


print(MemorySaver is InMemorySaver)