from collections.abc import Callable
from typing import Any

from app.agents.reflection.nodes import create_reflect_node
from app.agents.reflection.state import ReflectionState


def build_reflection_graph(reflector: Callable[[str], str]) -> Any:
    from langgraph.graph import END, START, StateGraph

    builder = StateGraph(ReflectionState)
    builder.add_node("reflect", create_reflect_node(reflector))
    builder.add_edge(START, "reflect")
    builder.add_edge("reflect", END)
    return builder.compile()
