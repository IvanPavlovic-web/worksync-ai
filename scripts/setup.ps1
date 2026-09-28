$ErrorActionPreference = "Stop"
foreach ($tool in @("python", "node", "docker")) { if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool is required" } }
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
& .\.venv\Scripts\python.exe -m playwright install chromium
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
docker compose up -d postgres redis meilisearch
Push-Location frontend; npm ci; Pop-Location

