#!/usr/bin/env bash
docker compose down
pkill -f "uvicorn app.main" || true
pkill -f "next dev" || true
pkill -f "celery -A" || true

