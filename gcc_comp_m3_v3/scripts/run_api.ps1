# Start API server with environment setup
# L3 M3.3: Audit Logging & SIEM Integration

Write-Host "Starting L3 M3.3 Audit Logging API..." -ForegroundColor Green

# Set Python path to include project root
$env:PYTHONPATH = $PWD

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "Warning: .env file not found. Using defaults from .env.example" -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env and configure your settings" -ForegroundColor Yellow
}

# Start uvicorn server
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
