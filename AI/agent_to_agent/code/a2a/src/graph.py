from langgraph.graph import StateGraph, START, END

from nodes import compute, escalate, summarize
from state import ExpenseState

from collector import MAX_STEPS, build_collector

def next_step(state: ExpenseState) -> str:
    if state["steps"] >= MAX_STEPS:
        return "compute"
    return "tools" if state["messages"][-1].tool_calls else "compute"

def after_compute(state: ExpenseState) -> str:
    return "escalate" if state["violations"] else "summarize"

def collect(state: ExpenseState) -> dict:
    result = build_collector().invoke({
        "trip_id": state["trip_id"],
        "messages": [],
        "steps": 0,
        "log": [],
    })
    return {
        "receipts": result["receipts"],
        "rates": result.get("rates") or {},
        "log": [f"수집기가 영수증 {len(result['receipts'])}건, 환율 {len(result.get('rates') or {})}건 가져옴"],
    }

def build_graph(checkpointer=None):
    builder = StateGraph(ExpenseState)
    builder.add_node("collect", collect)
    builder.add_node("compute", compute)
    builder.add_node("escalate", escalate)
    builder.add_node("summarize", summarize)

    builder.add_edge(START, "collect")
    builder.add_edge("collect", "compute")
    builder.add_conditional_edges("compute", after_compute,
                                  {"escalate": "escalate", "summarize": "summarize"})
    builder.add_edge("escalate", END)
    builder.add_edge("summarize", END)

    return builder.compile(checkpointer=checkpointer)

# def build_graph(checkpointer=None):
#     builder = StateGraph(ExpenseState)
#     builder.add_node("plan", plan)
#     builder.add_node("tools", run_tools)
#     builder.add_node("compute", compute)
#     builder.add_node("escalate", escalate)
#     builder.add_node("summarize", summarize)

#     # builder.add_node("collect", build_collector())

#     builder.add_edge(START, "plan")
#     builder.add_conditional_edges("plan", next_step, {"tools": "tools", "compute": "compute"})
#     builder.add_edge("tools", "plan")
#     builder.add_conditional_edges("compute", after_compute,
#                                   {"escalate": "escalate", "summarize": "summarize"})
#     builder.add_edge("escalate", END)
#     builder.add_edge("summarize", END)

#     return builder.compile(checkpointer = checkpointer)