from celery import Celery
import os

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", broker_url)

celery_app = Celery(
    "cardio_classifier",
    broker=broker_url,
    backend=backend_url,
)

celery_app.conf.update(task_track_started=True, result_expires=3600)
