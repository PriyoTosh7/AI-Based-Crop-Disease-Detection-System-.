$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $cmd) { Write-Host "Python was not found. Install Python 3.11/3.12." -ForegroundColor Red; exit 1 }
    $python = $cmd.Source
}

Write-Host "Starting the integrated FastAPI app (frontend + backend + API)..." -ForegroundColor Cyan
Write-Host "Development URL: http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "API docs:        http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "The teacher demo must use the public HTTPS deployment URL." -ForegroundColor Green
& $python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
