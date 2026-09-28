#!/usr/bin/env bash
set -euo pipefail
command -v python3 >/dev/null || { echo "Python 3 is required"; exit 1; }
command -v node >/dev/null || { echo "Node.js is required"; exit 1; }
command -v docker >/dev/null || { echo "Docker is required"; exit 1; }
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$python_version" != "3.12" ]; then echo "Python 3.12 is required. Found Python $python_version."; exit 1; fi
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m playwright install chromium
python -m spacy download xx_ent_wiki_sm
test -f backend/.env || cp backend/.env.example backend/.env
test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local
docker compose up -d postgres redis meilisearch
(cd frontend && npm ci)

