from collections.abc import Callable

from app.agents.reflection.state import ReflectionState


def create_reflect_node(reflector: Callable[[str], str]):
    def reflect(state: ReflectionState) -> ReflectionState:
        return {"result": reflector(state["subject"])}

    return reflect

