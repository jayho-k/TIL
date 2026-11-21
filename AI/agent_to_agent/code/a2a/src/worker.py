import os

from card import AGENT_CARD

from langgraph.checkpoint.postgres import PostgresSaver

from fastapi import FastAPI
from pydantic import BaseModel

from collector import build_collector

app = FastAPI()


class RunRequest(BaseModel):
    trip_id: str


# @app.post("/run")
# def run(req: RunRequest):
#     result = build_collector().invoke(
#         {
#             "trip_id": req.trip_id,
#             "messages": [],
#             "steps": 0,
#             "log": [],
#         }
#     )
#     return result

@app.post("/run")
def run(req: RunRequest):
    result = build_collector().invoke(
        {
            "trip_id": req.trip_id,
            "messages": [],
            "steps": 0,
            "log": [],
        }
    )
    return {
        "receipts": result["receipts"],
        "rates": result.get("rates") or {},
    }

@app.get("/.well-known/agent-card.json")
def agent_card():
    return AGENT_CARD

@app.get("/debug/state/{thread_id}")
def debug_state(thread_id: str):
    with PostgresSaver.from_conn_string(os.environ["POSTGRES_URL"]) as saver:
        from graph import build_graph

        snapshot = build_graph(checkpointer=saver).get_state(
            {"configurable": {"thread_id": thread_id}}
        )

    if not snapshot.values:
        return {"found": False}

    return {
        "found": True,
        "values": snapshot.values,
        "next": list(snapshot.next),
    }