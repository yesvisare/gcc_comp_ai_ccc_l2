# Start API server for L3 M4.2: Vendor Risk Assessment
# Windows PowerShell script

Write-Host "Starting Vendor Risk Assessment API..." -ForegroundColor Green

# Set Python path to current directory
$env:PYTHONPATH = $PWD

# Start uvicorn server
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
