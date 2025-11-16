# PowerShell script to start the FastAPI server
# L3 M2: Security_Access_Control

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  L3 M2: Security_Access_Control" -ForegroundColor Cyan
Write-Host "  Authentication & Identity Management API" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for development mode
$env:PYTHONPATH = $PWD
$env:ENVIRONMENT = "development"
$env:DEBUG_MODE = "true"
$env:LOG_LEVEL = "INFO"

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "   Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "   ✓ Created .env file" -ForegroundColor Green
    Write-Host "   Please edit .env with your OAuth credentials" -ForegroundColor Yellow
    Write-Host ""
}

# Check if virtual environment is activated
if (-Not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Warning: Virtual environment not activated" -ForegroundColor Yellow
    Write-Host "   Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
}

# Display startup information
Write-Host "Starting API server..." -ForegroundColor Green
Write-Host "  • Host: 0.0.0.0" -ForegroundColor White
Write-Host "  • Port: 8000" -ForegroundColor White
Write-Host "  • Reload: Enabled (development mode)" -ForegroundColor White
Write-Host "  • Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""

# Check if port 8000 is already in use
$portInUse = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
if ($portInUse) {
    Write-Host "⚠️  Warning: Port 8000 is already in use" -ForegroundColor Yellow
    Write-Host "   Kill the existing process or use a different port" -ForegroundColor Yellow
    Write-Host ""
}

# Start uvicorn server
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

try {
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
}
catch {
    Write-Host ""
    Write-Host "❌ Error starting server: $_" -ForegroundColor Red
    exit 1
}
