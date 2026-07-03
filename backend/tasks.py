"""Celery background tasks for async content generation."""
from __future__ import annotations

import asyncio
import json

from celery import Task

from app.celery_app import celery_app
from app.config import settings
from app.database import SessionLocal
from app.models.sqlalchemy_models import ContentPackage

logger = logging.getLogger(__name__)


class AsyncTask(Task):
    def run_async(self, coro):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

