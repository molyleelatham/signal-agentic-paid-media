"""Celery tasks for SIGNAL platform."""

from shared.tasks.celery_app import celery_app

__all__ = ["celery_app"]