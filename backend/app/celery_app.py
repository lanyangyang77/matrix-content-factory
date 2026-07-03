"""Celery application configuration."""
from __future__ import annotations

from celery import Celery

from app.config import settings

celery_app = Celery(
    "matrix_biz",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["tasks"],
)

# Development: run tasks synchronously (no Redis needed)
task_always_eager = settings.app_env == "development"

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_ignore_result=False,
    result_expires=3600 * 24,
    worker_max_tasks_per_child=100,
    task_always_eager=task_always_eager,
    task_eager_propagates=True,
)
