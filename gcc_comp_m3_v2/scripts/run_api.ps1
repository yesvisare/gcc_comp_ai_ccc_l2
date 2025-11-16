# Start API server with environment setup
# L3 M3.2: Automated Compliance Testing

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M3.2: Automated Compliance Testing API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include project root
$env:PYTHONPATH = $PWD

# Service Configuration (detected: OPA + optional Presidio)
Write-Host "Configuring services..." -ForegroundColor Yellow

# OPA Configuration (requires binary installation)
# Download from: https://www.openpolicyagent.org/docs/latest/
$env:OPA_ENABLED = "False"  # Set to "True" if OPA binary installed
$env:OPA_BINARY_PATH = "opa"
$env:OPA_POLICY_PATH = "./policies"

# Presidio Configuration (optional - requires pip install)
$env:PRESIDIO_ENABLED = "False"  # Set to "True" after: pip install presidio-analyzer presidio-anonymizer

# Logging
$env:LOG_LEVEL = "INFO"

# Check for .env file
if (Test-Path ".env") {
    Write-Host "✓ Loading configuration from .env file" -ForegroundColor Green
} else {
    Write-Host "⚠ No .env file found - using defaults" -ForegroundColor Yellow
    Write-Host "  Create .env from .env.example for custom configuration" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
Write-Host "  OPA_ENABLED: $env:OPA_ENABLED" -ForegroundColor Gray
Write-Host "  PRESIDIO_ENABLED: $env:PRESIDIO_ENABLED" -ForegroundColor Gray
Write-Host ""

# Start FastAPI server
Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "  Host: 0.0.0.0" -ForegroundColor Gray
Write-Host "  Port: 8000" -ForegroundColor Gray
Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
