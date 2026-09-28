$env:PYTHONPATH = "backend"
& .\.venv\Scripts\python.exe -c "from app.database import init_db; init_db(); print('Database schema ready')"

