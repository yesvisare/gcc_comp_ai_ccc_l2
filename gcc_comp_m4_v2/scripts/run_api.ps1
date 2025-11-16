# Start API server with environment setup
# Windows PowerShell script for L3 M4.2: Vendor Risk Assessment

Write-Host "=== L3 M4.2: Vendor Risk Assessment API ===" -ForegroundColor Green
Write-Host ""

# Set PYTHONPATH to include project root
$env:PYTHONPATH = $PWD.Path

# Set environment variables
$env:ENVIRONMENT = "development"
$env:LOG_LEVEL = "INFO"

Write-Host "Starting FastAPI server..." -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Interactive docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
try {
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
}
catch {
    Write-Host "Error starting API server: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you have installed dependencies:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}
