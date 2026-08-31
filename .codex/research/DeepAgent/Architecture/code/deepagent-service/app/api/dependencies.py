from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request

from app.agents.registry import AgentRegistry
from app.services.reflection_service import ReflectionService


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    agents: AgentRegistry
    reflections: ReflectionService


def get_container(request: Request) -> ApplicationContainer:
    return request.app.state.container


ContainerDependency = Annotated[ApplicationContainer, Depends(get_container)]

