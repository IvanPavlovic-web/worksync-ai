#!/usr/bin/env bash
PYTHONPATH=backend .venv/bin/celery -A app.workers.celery_app.celery call app.workers.tasks.scrape_tier --args='["critical"]'

