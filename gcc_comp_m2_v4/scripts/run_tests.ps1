# Run tests with pytest
# All tests run in offline mode by default

Write-Host "Running L3 M2.4 Security Testing Test Suite..." -ForegroundColor Green

# Set PYTHONPATH to include project root
$env:PYTHONPATH = $PWD

# Force offline mode for tests
$env:OFFLINE = "true"
$env:OPENAI_ENABLED = "false"
$env:PINECONE_ENABLED = "false"

Write-Host "Test Configuration:" -ForegroundColor Cyan
Write-Host "  OFFLINE: $env:OFFLINE" -ForegroundColor Yellow
Write-Host "  Test directory: tests/" -ForegroundColor Yellow
Write-Host ""

# Run pytest with verbose output
Write-Host "Executing pytest..." -ForegroundColor Cyan
pytest -v tests/

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Some tests failed. See output above." -ForegroundColor Red
    exit $LASTEXITCODE
}
