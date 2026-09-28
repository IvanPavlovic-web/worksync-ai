#!/usr/bin/env bash
set -euo pipefail
command -v python3; command -v node; command -v docker
docker compose ps
PYTHONPATH=backend .venv/bin/python -c 'from app.main import app; print("Backend imports: OK")'

