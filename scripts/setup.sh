#!/usr/bin/env bash
set -euo pipefail
command -v python3 >/dev/null || { echo "Python 3 is required"; exit 1; }
command -v node >/dev/null || { echo "Node.js is required"; exit 1; }
command -v docker >/dev/null || { echo "Docker is required"; exit 1; }
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m playwright install chromium
test -f backend/.env || cp backend/.env.example backend/.env
test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local
docker compose up -d postgres redis meilisearch
(cd frontend && npm ci)

