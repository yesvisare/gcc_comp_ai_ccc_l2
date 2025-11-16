# Start FastAPI server for L3 M1.4: Compliance Documentation & Evidence
# Windows PowerShell script

Write-Host "Starting L3 M1.4: Compliance Documentation & Evidence API..." -ForegroundColor Cyan
Write-Host ""

# Set environment variables (if needed)
# Note: For production, use .env file instead
# $env:POSTGRES_PASSWORD = "your_password"
# $env:AWS_ACCESS_KEY_ID = "your_key"
# $env:AWS_SECRET_ACCESS_KEY = "your_secret"

# Set Python path to include project root
$env:PYTHONPATH = $PWD

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - PostgreSQL: Use .env file for credentials" -ForegroundColor Gray
Write-Host "  - AWS S3: Use .env file for credentials" -ForegroundColor Gray
Write-Host "  - Running in offline mode if credentials not provided" -ForegroundColor Gray
Write-Host ""

Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
