# backend/app/celery_app.py
from celery import Celery
from app.config import settings

celery_app = Celery(
    "brickfarm_tasks",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_routes={"tasks.*": {"queue": "default"}},
    worker_prefetch_multiplier=1,
)
