@echo off
cd /d %~dp0

echo Starting FastAPI backend on http://0.0.0.0:8000 ...
start "RVC Backend" cmd /k ".\\venv\\Scripts\\activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo Starting Next.js frontend (production) on http://0.0.0.0:3001 ...
start "RVC Frontend" cmd /k "cd frontend && npm start -- --port 3001 --hostname 0.0.0.0"

echo.
echo Both servers are starting up.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3001
echo   Smartphone (same Wi-Fi): http://^<this PC LAN IP^>:3001
echo.
echo NOTE: After code changes, run  cd frontend ^&^& npm run build  before restarting.
echo.
pause
