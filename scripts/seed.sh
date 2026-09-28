#!/usr/bin/env bash
set -euo pipefail
PYTHONPATH=backend .venv/bin/python -c 'from app.database import Base, engine; Base.metadata.create_all(engine); print("Database schema ready")'

