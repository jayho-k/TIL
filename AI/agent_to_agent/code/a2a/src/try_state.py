from langgraph.graph import StateGraph, START, END
from state import ExpenseState

def first(state: ExpenseState) -> dict:
    return {"total": 100, "log": ["first가 씀"]}

def second(state: ExpenseState) -> dict:
    return {"total": 200, "log": ["second가 씀"]}

builder = StateGraph(ExpenseState)
builder.add_node("first", first)
builder.add_node("second", second)
builder.add_edge(START, "first")
builder.add_edge("first", "second")
builder.add_edge("second", END)
graph = builder.compile()

result = graph.invoke({"trip_id": "T-2026-03", "log": []})
print("total:", result["total"])
print("log:", result["log"])