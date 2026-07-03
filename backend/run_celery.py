#!/usr/bin/env python
"""Celery worker launch script."""
from app.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start(argv=["celery", "worker", "-A", "app.celery_app", "-l", "info", "-P", "solo"])
