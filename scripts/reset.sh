#!/usr/bin/env bash
set -euo pipefail
docker compose down -v
./scripts/setup.sh

