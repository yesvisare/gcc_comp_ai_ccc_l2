# Start FastAPI server for L3 M4.4 Compliance Maturity API
# This module runs fully offline - no external services required

Write-Host "Starting L3 M4.4 Compliance Maturity API..." -ForegroundColor Green
Write-Host ""

# Set PYTHONPATH to include src directory
$env:PYTHONPATH = $PWD

# Optional: Enable Prometheus/Grafana (uncomment if needed)
# $env:PROMETHEUS_ENABLED = "True"
# $env:PROMETHEUS_GATEWAY = "http://localhost:9091"
# $env:GRAFANA_ENABLED = "True"
# $env:GRAFANA_URL = "http://localhost:3000"

# Set log level
$env:LOG_LEVEL = "INFO"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  PYTHONPATH: $env:PYTHONPATH"
Write-Host "  Mode: Offline (Local Processing)"
Write-Host "  Prometheus: Disabled (optional - for production dashboards)"
Write-Host "  Grafana: Disabled (optional - for production dashboards)"
Write-Host ""
Write-Host "Starting uvicorn server on http://0.0.0.0:8000..." -ForegroundColor Yellow
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000 --log-level info
