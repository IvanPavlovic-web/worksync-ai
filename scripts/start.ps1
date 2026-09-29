$root = (Resolve-Path "$PSScriptRoot\..").Path
docker compose up -d postgres redis meilisearch
Start-Process powershell -ArgumentList @("-NoExit", "-Command", "Set-Location -LiteralPath '$root\backend'; `$env:PYTHONPATH='$root\backend'; & '$root\.venv\Scripts\python.exe' -m uvicorn app.main:app --reload --port 8000")
Start-Process powershell -ArgumentList @("-NoExit", "-Command", "Set-Location -LiteralPath '$root\frontend'; npm run dev")
# Windows does not support Celery's prefork pool reliably. The solo pool keeps
# the worker in one process and avoids WinError 5 from spawned child workers.
Start-Process powershell -ArgumentList @("-NoExit", "-Command", "Set-Location -LiteralPath '$root\backend'; `$env:PYTHONPATH='$root\backend'; & '$root\.venv\Scripts\python.exe' -m celery -A app.workers.celery_app.celery worker -l info --pool=solo")
Start-Process powershell -ArgumentList @("-NoExit", "-Command", "Set-Location -LiteralPath '$root\backend'; `$env:PYTHONPATH='$root\backend'; & '$root\.venv\Scripts\python.exe' -m celery -A app.workers.celery_app.celery beat -l info")

