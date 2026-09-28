docker compose up -d postgres redis meilisearch
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; & '$PWD\.venv\Scripts\Activate.ps1'; uvicorn app.main:app --reload --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; & '$PWD\.venv\Scripts\Activate.ps1'; celery -A app.workers.celery_app.celery worker -l info"

