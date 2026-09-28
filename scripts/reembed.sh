PYTHONPATH=backend .venv/bin/celery -A app.workers.celery_app.celery call app.workers.tasks.reembed_all_jobs

