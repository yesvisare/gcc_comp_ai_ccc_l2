# Run tests with pytest
# L3 M3.3: Audit Logging & SIEM Integration

Write-Host "Running L3 M3.3 Audit Logging Tests..." -ForegroundColor Green

# Set Python path to include project root
$env:PYTHONPATH = $PWD

# Run pytest with verbose output
Write-Host ""
Write-Host "Running test suite..." -ForegroundColor Cyan
Write-Host ""

pytest tests/ -v --tb=short

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Some tests failed. Check output above." -ForegroundColor Red
    exit $LASTEXITCODE
}
