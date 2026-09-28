Get-Command python,node,docker
docker compose ps
$env:PYTHONPATH = "backend"
& .\.venv\Scripts\python.exe -c "from app.main import app; print('Backend imports: OK')"

