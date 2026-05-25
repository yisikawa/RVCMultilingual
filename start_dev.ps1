# バックエンドとフロントエンドを起動するスクリプト
Write-Host "Installing Python dependencies..."
.\venv\Scripts\pip install fastapi uvicorn[standard] python-multipart -q

Write-Host ""
Write-Host "Starting FastAPI backend on http://localhost:8000 ..."
Start-Process -NoNewWindow -FilePath ".\venv\Scripts\uvicorn.exe" -ArgumentList "backend.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir backend --reload-dir core"

Write-Host "Starting Next.js frontend on https://localhost:3000 ..."
Write-Host "For phones/tablets on the same Wi-Fi, open https://<this PC's LAN IP>:3000"
Write-Host "Note: iPhone voice input requires Safari (not Chrome/Firefox) and HTTPS."
Set-Location frontend
npm run dev
