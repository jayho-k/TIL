# import sys

# from graph import build_graph

# trip = sys.argv[1] if len(sys.argv) > 1 else "T-2026-04"
# graph = build_graph()
# result = graph.invoke({"trip_id": trip, "log": []})

# print("합계:", result["total"])
# print("위반:", result["violations"] or "없음")
# print("보고:", result["report"])
# print("부모 상태 키:", sorted(result))
# print("기록:")
# for line in result["log"]:
#     print(" -", line)

import sys

from graph import build_graph

trip = sys.argv[1] if len(sys.argv) > 1 else "T-2026-04"
graph = build_graph()
start = {"trip_id": trip, "log": []}

print("--- 부모만 ---")
for chunk in graph.stream(start, stream_mode="updates"):
    for node, update in chunk.items():
        print(f"  {node}: {sorted(update) if isinstance(update, dict) else update}")

print()
print("--- 수집기 안까지 ---")
for path, chunk in graph.stream(start, stream_mode="updates", subgraphs=True):
    where = "부모" if not path else path[0].split(":")[0]
    for node, update in chunk.items():
        print(f"  [{where}] {node}: {sorted(update) if isinstance(update, dict) else update}")