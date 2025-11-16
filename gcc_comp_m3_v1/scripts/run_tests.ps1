# Run tests with pytest
# Ensures PYTHONPATH is set correctly and runs in offline mode

Write-Host "Running GCC Compliance Monitoring Tests..." -ForegroundColor Green

# Set PYTHONPATH to project root
$env:PYTHONPATH = $PWD

# Force offline mode for tests
$env:OFFLINE = "true"
$env:PROMETHEUS_ENABLED = "false"
$env:GRAFANA_ENABLED = "false"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  PYTHONPATH: $env:PYTHONPATH"
Write-Host "  OFFLINE: $env:OFFLINE"
Write-Host ""

# Run pytest with verbose output
pytest -v tests/

Write-Host ""
Write-Host "Tests completed!" -ForegroundColor Green
