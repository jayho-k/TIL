import operator
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from nodes import model
from tools import ALL_TOOLS

MAX_STEPS = 6

planner = model.bind_tools([t for t in ALL_TOOLS if t.name != "check_policy"])
by_name = {t.name: t for t in ALL_TOOLS}

class CollectorState(TypedDict):
    trip_id: str
    messages: Annotated[list, add_messages] # list
    steps: int
    receipts: list[dict]
    rates: dict
    log: Annotated[list[str], operator.add]


def plan(state: CollectorState) -> dict:
    msgs = state.get("messages") or [HumanMessage(
        f"출장 {state['trip_id']}의 영수증을 가져오세요. "
        "외화로 된 항목이 있으면 그 통화의 환율도 가져오세요. "
        "필요한 자료를 다 모았으면 도구를 더 부르지 말고 '완료'라고만 답하세요."
    )]
    ai = planner.invoke(msgs)
    new = msgs + [ai] if not state.get("messages") else [ai]
    return {"messages": new, "steps": state.get("steps", 0) + 1}

def run_tools(state: CollectorState) -> dict:
    ai = state["messages"][-1]
    out = {"messages": [], "log": []}
    for tc in ai.tool_calls:
        result = by_name[tc["name"]].invoke(tc["args"])
        out["messages"].append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
        out["log"].append(f"{tc['name']}({tc['args']}) 호출")
        if tc["name"] == "list_receipts":
            out["receipts"] = result
        elif tc["name"] == "get_rate":
            rates = dict(state.get("rates") or {})
            rates[tc["args"]["currency"].upper()] = result
            out["rates"] = rates
    return out

def next_step(state: CollectorState) -> str:
    if state["steps"] >= MAX_STEPS:
        return "done"
    return "tools" if state["messages"][-1].tool_calls else "done"

def build_collector():
    builder = StateGraph(CollectorState)
    builder.add_node("plan", plan)
    builder.add_node("tools", run_tools)
    builder.add_edge(START, "plan")
    builder.add_conditional_edges("plan", next_step, {"tools": "tools", "done": END})
    builder.add_edge("tools", "plan")
    return builder.compile()