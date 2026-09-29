$ErrorActionPreference = "Stop"
foreach ($tool in @("python", "node", "docker")) { if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool is required" } }
$pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($pythonVersion -notin @("3.12", "3.13")) { throw "Python 3.12 or 3.13 is required. Found Python $pythonVersion. Install a supported Python version and run setup again." }
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
& .\.venv\Scripts\python.exe -m playwright install chromium
& .\.venv\Scripts\python.exe -m spacy download xx_ent_wiki_sm
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
if (-not (Test-Path frontend\.env.local)) { Copy-Item frontend\.env.example frontend\.env.local }
docker compose up -d postgres redis meilisearch
Push-Location frontend; npm ci; Pop-Location

