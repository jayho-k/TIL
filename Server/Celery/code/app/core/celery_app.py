from celery import Celery
from app.core.config import settings
from app.container import Container

celery_app = Celery(
    "worker", 
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    "app.tasks.user_tasks.send_welcome_email": "main-queue"
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Instantiate container for injection in tasks
container = Container()
container.wire(modules=["app.tasks.user_tasks"])

# Auto-discover tasks from defined packages
# We can explicitily list 'app.tasks.user_tasks' in include, or use autodiscover mechanism.
# Since we are using shared_task, imports are enough if wired, but lets be explicit.
celery_app.conf.update(
    include=["app.tasks.user_tasks"]
)
# celery_app.autodiscover_tasks(['app.tasks']) # Option if we had tasks.py in packages
