#!/usr/bin/env bash
set -euo pipefail
PYTHONPATH=backend .venv/bin/python -c 'from app.database import init_db; init_db(); print("Database schema ready")'

