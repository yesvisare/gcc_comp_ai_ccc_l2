# Start API server for L3 M2.2: Authorization & Multi-Tenant Access Control
# Windows PowerShell script

Write-Host "Starting L3 M2.2 Authorization & Multi-Tenant Access Control API..." -ForegroundColor Green
Write-Host ""

# Set Python path
$env:PYTHONPATH = $PWD

# Load environment variables from .env if it exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            Set-Item -Path "env:$name" -Value $value
        }
    }
} else {
    Write-Host "⚠️  No .env file found. Using default configuration (offline mode)." -ForegroundColor Yellow
    Write-Host "   Copy .env.example to .env and configure your credentials." -ForegroundColor Yellow
    Write-Host ""

    # Set default environment variables for offline mode
    $env:PINECONE_ENABLED = "false"
    $env:POSTGRES_ENABLED = "false"
    $env:OPA_ENABLED = "false"
}

# Display service status
Write-Host "Service Configuration:" -ForegroundColor Cyan
Write-Host "  Pinecone: $env:PINECONE_ENABLED" -ForegroundColor Gray
Write-Host "  PostgreSQL: $env:POSTGRES_ENABLED" -ForegroundColor Gray
Write-Host "  OPA: $env:OPA_ENABLED" -ForegroundColor Gray
Write-Host ""

# Start uvicorn server
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
