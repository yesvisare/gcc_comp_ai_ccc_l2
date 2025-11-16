# Start API Server for L3 M1.4: Compliance Documentation & Evidence
# Windows PowerShell script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M1.4: Compliance Documentation & Evidence" -ForegroundColor Cyan
Write-Host "Starting FastAPI Server..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to project root
$env:PYTHONPATH = $PWD.Path

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Please edit .env with your PostgreSQL and AWS credentials" -ForegroundColor Green
    Write-Host ""
}

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "Run: python -m venv venv" -ForegroundColor Yellow
    Write-Host "Then: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "Then: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
}

# Display configuration info
Write-Host "Configuration:" -ForegroundColor Green
Write-Host "  - Mode: OFFLINE (no external AI services)" -ForegroundColor Gray
Write-Host "  - PostgreSQL: Check .env for credentials" -ForegroundColor Gray
Write-Host "  - AWS S3: Check .env for evidence storage" -ForegroundColor Gray
Write-Host ""

Write-Host "API Endpoints:" -ForegroundColor Green
Write-Host "  - Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor Gray
Write-Host "  - Health: http://localhost:8000/health" -ForegroundColor Gray
Write-Host ""

Write-Host "Starting server on http://0.0.0.0:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server
try {
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
}
catch {
    Write-Host "❌ Failed to start server" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Install dependencies: pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host "  2. Check .env configuration" -ForegroundColor Gray
    Write-Host "  3. Ensure port 8000 is not in use" -ForegroundColor Gray
    exit 1
}
