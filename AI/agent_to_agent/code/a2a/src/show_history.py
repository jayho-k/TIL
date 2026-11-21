import os

from langgraph.checkpoint.postgres import PostgresSaver

from graph import build_graph

with PostgresSaver.from_conn_string(os.environ["POSTGRES_URL"]) as saver:
    graph = build_graph(checkpointer=saver)
    config = {"configurable": {"thread_id": "trip-3"}}

    snapshot = graph.get_state(config)
    if not snapshot.values:
        print("저장된 상태 없음")
    else:
        print("합계:", snapshot.values["total"])
        print("위반:", len(snapshot.values["violations"]), "건")
        print()
        print("체크포인트 이력 (최신부터):")
        for snap in graph.get_state_history(config):
            step = snap.metadata["step"]
            nxt = snap.next or ("끝",)
            print(f"  step {step:>2} · 다음 노드 {nxt}")