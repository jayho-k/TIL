from app.repositories.user_repository import UserRepository
from app.models.user import User

class UserService:
    def __init__(self, user_repository: UserRepository):
        self._repository = user_repository

    async def get_user(self, user_id: int) -> User:
        return await self._repository.get_by_id(user_id)

    async def create_new_user(self, email: str, password: str) -> User:
        user = await self._repository.create_user(email, password)
        # Trigger Celery Task
        # Import inside method to avoid circular dependency with container -> user_service -> user_tasks -> container
        from app.tasks.user_tasks import send_welcome_email
        await send_welcome_email.delay(user.email)
        return user
