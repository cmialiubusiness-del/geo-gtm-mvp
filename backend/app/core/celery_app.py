from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "geo_gtm_mvp",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=False,
    beat_schedule={
        "nightly-collection-all-orgs": {
            "task": "app.tasks.run_nightly_all_orgs",
            "schedule": crontab(hour=2, minute=0),
        }
    },
)
