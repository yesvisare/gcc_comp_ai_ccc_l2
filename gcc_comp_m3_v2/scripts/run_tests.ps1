# Run compliance test suite with pytest
# L3 M3.2: Automated Compliance Testing

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M3.2: Compliance Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include project root
$env:PYTHONPATH = $PWD

Write-Host "Test Configuration:" -ForegroundColor Yellow
Write-Host "  Test Directory: tests/" -ForegroundColor Gray
Write-Host "  Coverage Target: 95%" -ForegroundColor Gray
Write-Host "  Test Pyramid: 70% Unit, 20% Integration, 10% E2E" -ForegroundColor Gray
Write-Host ""

# Check if pytest is installed
Write-Host "Checking pytest installation..." -ForegroundColor Yellow
python -m pytest --version 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ pytest not found - installing..." -ForegroundColor Red
    pip install pytest pytest-cov pytest-asyncio
    Write-Host ""
}

# Run tests with coverage
Write-Host "Running compliance tests..." -ForegroundColor Yellow
Write-Host ""

pytest tests/ -v --tb=short --cov=src/l3_m3_monitoring_reporting --cov-report=term-missing --cov-report=html

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test execution completed" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Coverage report saved to: htmlcov/index.html" -ForegroundColor Gray
Write-Host ""

# Show exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed - see output above" -ForegroundColor Red
}

exit $LASTEXITCODE
