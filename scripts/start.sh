#!/usr/bin/env bash
set -euo pipefail
docker compose up -d postgres redis meilisearch
(cd backend && . ../.venv/bin/activate && uvicorn app.main:app --reload --port 8000) &
(cd frontend && npm run dev) &
(cd backend && . ../.venv/bin/activate && celery -A app.workers.celery_app.celery worker -l info) &
wait

