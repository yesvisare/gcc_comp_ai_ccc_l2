# Start API server with environment setup
# No external services required - all processing is local

$env:PYTHONPATH = $PWD
$env:ENVIRONMENT = "development"
$env:LOG_LEVEL = "INFO"

Write-Host "Starting L3 M3.4 Incident Response API..." -ForegroundColor Green
Write-Host "Environment: development" -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
