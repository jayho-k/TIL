import os

from langgraph.checkpoint.postgres import PostgresSaver

from graph import build_graph

with PostgresSaver.from_conn_string(os.environ["POSTGRES_URL"]) as saver:
    saver.setup() # relation "checkpoints" does not exist
    graph = build_graph(checkpointer=saver)
    config = {"configurable": {"thread_id": "trip-3"}}

    result = graph.invoke({"trip_id": "T-2026-03", "messages": [], "log": [], "steps": 0}, config)
    print("합계:", result["total"])