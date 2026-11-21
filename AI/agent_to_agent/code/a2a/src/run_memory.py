from langgraph.checkpoint.memory import MemorySaver

from graph import build_graph

saver = MemorySaver() # 메모리에 값을 담아.
graph = build_graph(checkpointer=saver)
config = {"configurable": {"thread_id": "trip-3"}}

result = graph.invoke({"trip_id": "T-2026-03", "messages": [], "log": [], "steps": 0}, config)
print("1회차 합계:", result["total"])

snapshot = graph.get_state(config)
print("저장된 합계:", snapshot.values["total"])
print("저장된 메시지 수:", len(snapshot.values["messages"]))
print("다음에 갈 노드:", snapshot.next)

for snap in graph.get_state_history(config):
    print(snap.metadata.get("step"), snap.next, snap.values.get("total"))


# import sys; sys.path.insert(0, 'src')
# from langgraph.checkpoint.memory import MemorySaver
# from graph import build_graph

# graph = build_graph(checkpointer=MemorySaver())
# print('trip-3:', graph.get_state({'configurable': {'thread_id': 'trip-3'}}).values)
# print('trip-9:', graph.get_state({'configurable': {'thread_id': 'trip-9'}}).values)