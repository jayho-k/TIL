import sys

from graph import build_graph

trip = sys.argv[1] if len(sys.argv) > 1 else "T-2026-03"
graph = build_graph()

for chunk in graph.stream({"trip_id": trip, "messages": [], "log": [], "steps": 0}):
    for node, update in chunk.items():
        if node == "plan":
            ai = update["messages"][-1]
            calls = [c["name"] for c in ai.tool_calls] or "없음"
            print(f"[plan] 스텝 {update['steps']} · 도구 요청: {calls}")
        elif node == "tools":
            print(f"[tools] {update['log']}")
        elif node == "compute":
            print(f"[compute] 합계 {update['total']} · 위반 {len(update['violations'])}건")
        else:
            print(f"[{node}] {update['report'][:60]}...")