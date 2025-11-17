# Run tests for L3 M4.4 Compliance Maturity module
# All tests run in offline mode (no external services required)

Write-Host "Running L3 M4.4 Compliance Maturity Tests..." -ForegroundColor Green
Write-Host ""

# Set PYTHONPATH to include src directory
$env:PYTHONPATH = $PWD

# Force offline mode for tests
$env:PROMETHEUS_ENABLED = "false"
$env:GRAFANA_ENABLED = "false"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  PYTHONPATH: $env:PYTHONPATH"
Write-Host "  Mode: Offline (No external services)"
Write-Host ""

# Run pytest with coverage
Write-Host "Running pytest..." -ForegroundColor Yellow
Write-Host ""

pytest tests/ -v --tb=short --color=yes

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "âœ" All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "âœ— Some tests failed. See output above for details." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "To run tests with coverage report:" -ForegroundColor Cyan
Write-Host "  pytest tests/ --cov=src --cov-report=html"
Write-Host ""
Write-Host "To run specific test file:" -ForegroundColor Cyan
Write-Host "  pytest tests/test_m4_compliance_maturity.py -v"
Write-Host ""
