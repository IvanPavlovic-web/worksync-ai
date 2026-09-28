$env:PYTHONPATH = "backend"
& .\.venv\Scripts\celery.exe -A app.workers.celery_app.celery call app.workers.tasks.scrape_tier --args='["critical"]'

