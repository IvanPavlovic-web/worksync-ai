@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Python environment is missing. Run scripts\setup.ps1 first.
  pause
  exit /b 1
)
if not exist "frontend\node_modules" (
  echo Frontend dependencies are missing. Run scripts\setup.ps1 first.
  pause
  exit /b 1
)

echo [WorkSync] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
  echo Docker Desktop is not running. Start Docker Desktop and run this file again.
  pause
  exit /b 1
)

if not exist "backend\.env" copy /Y "backend\.env.example" "backend\.env" >nul
if not exist "frontend\.env.local" copy /Y "frontend\.env.example" "frontend\.env.local" >nul

echo [WorkSync] Starting PostgreSQL, Redis and Meilisearch...
docker compose up -d postgres redis meilisearch
if errorlevel 1 (
  echo Docker services could not be started.
  pause
  exit /b 1
)

echo [WorkSync] Starting backend, Celery worker, Celery beat and frontend...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start.ps1"
echo.
echo WorkSync is starting:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API docs: http://localhost:8000/docs
pause
