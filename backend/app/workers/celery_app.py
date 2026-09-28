from celery import Celery
import app.workers.blog_tasks  # noqa
from app.config import settings


celery = Celery(
    "worksync",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery.conf.timezone = "UTC"
celery.conf.task_routes = {"app.workers.tasks.*": {"queue": "default"}}
celery.conf.beat_schedule = {
    "auto-blog": {
        "task": "app.workers.blog_tasks.generate_blog_batch",
        "schedule": 86400,   # jednom dnevno
        "kwargs": {"count": 3},
    },
    "scrape-critical": {
        "task": "app.workers.tasks.scrape_tier",
        "schedule": 1800,
        "kwargs": {"tier": "critical"},
    },
    "scrape-high": {
        "task": "app.workers.tasks.scrape_tier",
        "schedule": 7200,
        "kwargs": {"tier": "high"},
    },
    "scrape-medium": {
        "task": "app.workers.tasks.scrape_tier",
        "schedule": 21600,
        "kwargs": {"tier": "medium"},
    },
    "embed-missing": {
        "task": "app.workers.tasks.embed_missing_jobs",
        "schedule": 300,
    },
    "sync-meili": {
        "task": "app.workers.tasks.sync_meilisearch",
        "schedule": 600,
    },
    "deactivate-old": {
        "task": "app.workers.tasks.deactivate_old_jobs",
        "schedule": 86400,
    },
}
celery.autodiscover_tasks(["app.workers"])