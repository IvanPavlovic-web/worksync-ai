$env:PYTHONPATH = "backend"
& .\.venv\Scripts\python.exe -c "from app.database import Base, engine; Base.metadata.create_all(engine); print('Database schema ready')"

