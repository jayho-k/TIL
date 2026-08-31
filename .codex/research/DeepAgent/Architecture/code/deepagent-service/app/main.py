from fastapi import FastAPI

from app.agents.general.agent import LazyGeneralAgentRunner
from app.agents.registry import AgentRegistry
from app.api.dependencies import ApplicationContainer
from app.api.routes import agents, health, reflection_jobs
from app.core.config import Settings, get_settings
from app.models.document import Document
from app.prompts.registry import default_prompt_registry
from app.repositories.document_repository import InMemoryDocumentRepository
from app.repositories.reflection_job_repository import InMemoryReflectionJobRepository
from app.services.knowledge_service import KnowledgeService
from app.services.reflection_service import ReflectionService


def create_default_container(settings: Settings | None = None) -> ApplicationContainer:
    resolved_settings = settings or get_settings()
    documents = InMemoryDocumentRepository(
        [
            Document(
                id="architecture",
                title="Agent architecture",
                content="Agent tools call services; services depend on repository ports.",
            )
        ]
    )
    knowledge = KnowledgeService(documents)
    general = LazyGeneralAgentRunner(
        resolved_settings,
        default_prompt_registry(),
        knowledge,
    )
    return ApplicationContainer(
        agents=AgentRegistry({"general": general}),
        reflections=ReflectionService(InMemoryReflectionJobRepository()),
    )


def create_app(container: ApplicationContainer | None = None) -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name)
    application.state.container = container or create_default_container(settings)
    application.include_router(health.router)
    application.include_router(agents.router)
    application.include_router(reflection_jobs.router)
    return application


app = create_app()
