"""
Celery application for async task processing.

Handles background tasks such as:
- Periodic intelligence scanning
- Daily optimization routines
- Performance data processing
- Token calculations
- Agent execution for long-running operations
"""
from celery import Celery
from shared.utils.settings import settings

# Create Celery app
celery_app = Celery(
    "signal_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "shared.tasks.intelligence_tasks",
        "shared.tasks.trading_tasks",
        "shared.tasks.analytics_tasks",
        "shared.tasks.agent_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "daily-intelligence-scan": {
        "task": "shared.tasks.intelligence_tasks.run_daily_intelligence_scan",
        "schedule": 86400.0,  # Every 24 hours
    },
    "daily-optimization": {
        "task": "shared.tasks.trading_tasks.run_daily_optimization",
        "schedule": 86400.0,  # Every 24 hours
    },
    "hourly-performance-processing": {
        "task": "shared.tasks.analytics_tasks.process_hourly_performance",
        "schedule": 3600.0,  # Every hour
    },
    "token-calculations": {
        "task": "shared.tasks.analytics_tasks.calculate_token_rewards",
        "schedule": 21600.0,  # Every 6 hours
    },
}