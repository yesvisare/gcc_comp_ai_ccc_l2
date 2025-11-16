# Start API server with environment setup
# Services: PROMETHEUS (metrics) + GRAFANA (dashboards) + OPA (policy)

Write-Host "Starting GCC Compliance Monitoring API..." -ForegroundColor Green

# Set PYTHONPATH to project root
$env:PYTHONPATH = $PWD

# Optional: Enable Prometheus/Grafana if running locally
# Uncomment these lines if you have local instances running
# $env:PROMETHEUS_ENABLED = "True"
# $env:GRAFANA_ENABLED = "True"
# $env:OPA_ENABLED = "True"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  PYTHONPATH: $env:PYTHONPATH"
Write-Host "  PROMETHEUS_ENABLED: $env:PROMETHEUS_ENABLED"
Write-Host "  GRAFANA_ENABLED: $env:GRAFANA_ENABLED"
Write-Host ""
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Start uvicorn server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
