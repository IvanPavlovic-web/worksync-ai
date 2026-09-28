$root = (Resolve-Path "$PSScriptRoot\..").Path
docker compose up -d postgres redis meilisearch
Start-Process powershell -ArgumentList @("-NoExit", "-Command", "Set-Location -LiteralPath '$root\backend'; `$env:PYTHONPATH='$root\backend'; & '$root\.venv\Scripts\python.exe' -m uvicorn app.main:app --reload --port 8000")
Start-Process powershell -ArgumentList @("-NoExit", "-Command", "Set-Location -LiteralPath '$root\frontend'; npm run dev")
Start-Process powershell -ArgumentList @("-NoExit", "-Command", "Set-Location -LiteralPath '$root\backend'; `$env:PYTHONPATH='$root\backend'; & '$root\.venv\Scripts\python.exe' -m celery -A app.workers.celery_app.celery worker -l info")
Start-Process powershell -ArgumentList @("-NoExit", "-Command", "Set-Location -LiteralPath '$root\backend'; `$env:PYTHONPATH='$root\backend'; & '$root\.venv\Scripts\python.exe' -m celery -A app.workers.celery_app.celery beat -l info")

