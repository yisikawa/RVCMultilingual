# バックエンドとフロントエンドを起動するスクリプト
Write-Host "Installing Python dependencies..."
.\venv\Scripts\pip install fastapi uvicorn[standard] python-multipart -q

Write-Host ""
Write-Host "Starting FastAPI backend on http://localhost:8000 ..."
Start-Process -NoNewWindow -FilePath ".\venv\Scripts\uvicorn.exe" -ArgumentList "backend.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "Starting Next.js frontend on http://localhost:3000 ..."
Write-Host "For phones/tablets on the same Wi-Fi, open http://<this PC's LAN IP>:3000"
Set-Location frontend
npm run dev
