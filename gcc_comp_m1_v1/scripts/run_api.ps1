# PowerShell script to start the FastAPI server
# L3 M1.1: Why Compliance Matters in GCC RAG Systems

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M1.1 Compliance Risk Assessment API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to project root
$env:PYTHONPATH = $PWD.Path
Write-Host "✓ PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Green

# Optional: Enable services (set to "true" to enable)
# Uncomment and set your API key to enable OpenAI
# $env:PRESIDIO_ENABLED = "true"
# $env:OPENAI_ENABLED = "true"
# $env:OPENAI_API_KEY = "your-api-key-here"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  PRESIDIO_ENABLED: $env:PRESIDIO_ENABLED" -ForegroundColor Gray
Write-Host "  OPENAI_ENABLED: $env:OPENAI_ENABLED" -ForegroundColor Gray
Write-Host ""

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "✓ Found .env file" -ForegroundColor Green
} else {
    Write-Host "⚠ No .env file found. Copy .env.example to .env to configure API keys." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting API server..." -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "Interactive docs at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn with reload for development
uvicorn app:app --reload --host 0.0.0.0 --port 8000
