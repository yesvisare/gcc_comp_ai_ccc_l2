# Run tests for L3 M4.1: Model Cards & AI Governance
# All tests run offline - no external API dependencies

Write-Host "Running L3 M4.1 AI Governance Tests..." -ForegroundColor Cyan
Write-Host ""

# Set Python path to include project root
$env:PYTHONPATH = $PWD.Path

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - Mode: Local (offline testing)"
Write-Host "  - Python Path: $env:PYTHONPATH"
Write-Host "  - Test Suite: tests/test_m4_enterprise_integration.py"
Write-Host ""

# Run pytest with quiet mode
Write-Host "Executing tests..." -ForegroundColor Cyan
pytest -q tests/

Write-Host ""
Write-Host "Test run complete!" -ForegroundColor Green
Write-Host ""
Write-Host "For verbose output, run: pytest -v tests/" -ForegroundColor Yellow
Write-Host "For coverage report, run: pytest --cov=src tests/" -ForegroundColor Yellow
