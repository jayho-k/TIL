from dependency_injector import containers, providers
from app.core.database import async_session_factory
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

class Container(containers.DeclarativeContainer):
    
    wiring_config = containers.WiringConfiguration(modules=["app.api.endpoints"])

    db_session_factory = providers.Object(async_session_factory)

    # Repository
    user_repository = providers.Singleton(
        UserRepository,
        session_factory=db_session_factory,
    )

    # Service (Singleton)
    user_service = providers.Singleton(
        UserService,
        user_repository=user_repository,
    )
