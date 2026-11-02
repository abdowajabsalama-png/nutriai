Write-Host "========================================================" -ForegroundColor Green
Write-Host "               NutriAI Project Launcher                 " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

# 1. Check and start Backend (Port 8000)
$backendRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if (-not $backendRunning) {
    Write-Host "[*] Starting Backend Server (FastAPI)..." -ForegroundColor Yellow
    Start-Process cmd.exe -ArgumentList "/k cd /d `"$projectDir`" && venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
} else {
    Write-Host "[OK] Backend is already running on port 8000." -ForegroundColor Green
}

# 2. Check and start Frontend (Port 8501)
$frontendRunning = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if (-not $frontendRunning) {
    Write-Host "[*] Starting Frontend Server (Streamlit)..." -ForegroundColor Yellow
    Start-Process cmd.exe -ArgumentList "/k cd /d `"$projectDir`" && venv\Scripts\python.exe -m streamlit run frontend/app.py --server.port 8501"
} else {
    Write-Host "[OK] Frontend is already running on port 8501." -ForegroundColor Green
}

Write-Host ""
Write-Host "[*] Opening Project and API in browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# Open Frontend and API Documentation
Start-Process "http://localhost:8501"
Start-Process "http://127.0.0.1:8000/docs"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host " NutriAI is ready!" -ForegroundColor Green
Write-Host " - Frontend: http://localhost:8501" -ForegroundColor White
Write-Host " - API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
Start-Sleep -Seconds 3