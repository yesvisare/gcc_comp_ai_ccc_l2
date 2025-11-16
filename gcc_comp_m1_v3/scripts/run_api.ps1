# Start API server for L3 M1.3: Regulatory Frameworks Deep Dive
# OFFLINE mode - no external services required

Write-Host "Starting L3 M1.3 Compliance Analyzer API..." -ForegroundColor Green
Write-Host "Mode: OFFLINE (Local processing only)" -ForegroundColor Cyan

# Set environment variables
$env:PYTHONPATH = $PWD
$env:LOG_LEVEL = "INFO"
$env:MODE = "OFFLINE"

# Start FastAPI server
Write-Host "`nStarting uvicorn server on http://localhost:8000" -ForegroundColor Yellow
uvicorn app:app --reload --host 0.0.0.0 --port 8000
