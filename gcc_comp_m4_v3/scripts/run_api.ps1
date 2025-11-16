# Start FastAPI server for L3 M4.3: Change Management & Compliance
# No external API services required - internal governance tool

Write-Host "Starting Change Management API..." -ForegroundColor Green
Write-Host ""

# Set environment variables
$env:PYTHONPATH = $PWD
Write-Host "✓ PYTHONPATH set to: $PWD" -ForegroundColor Green

# Initialize database if needed
Write-Host "✓ Initializing database..." -ForegroundColor Green
python -c "from src.l3_m4_change_management import init_database; init_database()"

Write-Host ""
Write-Host "Starting API server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
