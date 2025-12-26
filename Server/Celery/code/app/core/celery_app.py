from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker", 
    broker=settings.CELERY_BROKER_URL, 
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.user_tasks"]
)

celery_app.conf.task_routes = {
    "send_welcome_email": "main-queue",
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
)
