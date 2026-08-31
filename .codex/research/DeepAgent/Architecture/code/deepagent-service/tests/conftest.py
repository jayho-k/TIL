from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.agents.registry import AgentRegistry
from app.api.dependencies import ApplicationContainer
from app.main import create_app
from app.repositories.reflection_job_repository import InMemoryReflectionJobRepository
from app.services.reflection_service import ReflectionService


class StubRunner:
    async def run(self, message: str, thread_id: str) -> str:
        return f"reply:{thread_id}:{message}"


@pytest.fixture
def client() -> Iterator[TestClient]:
    container = ApplicationContainer(
        agents=AgentRegistry({"general": StubRunner()}),
        reflections=ReflectionService(InMemoryReflectionJobRepository()),
    )
    with TestClient(create_app(container)) as test_client:
        yield test_client

