$env:PYTHONPATH = "backend"
& .\.venv\Scripts\celery.exe -A app.workers.celery_app.celery call app.workers.tasks.reembed_all_jobs

