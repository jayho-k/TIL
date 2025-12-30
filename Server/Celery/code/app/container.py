from dependency_injector import containers, providers
from app.core.database import async_session_factory
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

from app.core.database import create_session_factory

class InfraContainer(containers.DeclarativeContainer):
    config = providers.Configuration(yaml_files=["config.yaml"])
    
    db_session_factory = providers.Singleton(
        create_session_factory,
        db_url=config.db.url,
    )

    # Repository
    user_repository = providers.Singleton(
        UserRepository,
        session_factory=db_session_factory,
    )

InfraContainer.config.from_yaml("config.yaml")

class Container(containers.DeclarativeContainer):
    
    config = providers.Configuration(yaml_files=["config.yaml"])
    
    infra = providers.Container(
        InfraContainer,
        config=config,
    )

    # Service (Singleton)
    user_service = providers.Singleton(
        UserService,
        user_repository=infra.user_repository,
    )
