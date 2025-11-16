# Run tests with pytest
# Windows PowerShell script for L3 M4.2: Vendor Risk Assessment

Write-Host "=== L3 M4.2: Vendor Risk Assessment Test Suite ===" -ForegroundColor Green
Write-Host ""

# Set PYTHONPATH to include project root
$env:PYTHONPATH = $PWD.Path

Write-Host "Running tests with pytest..." -ForegroundColor Cyan
Write-Host ""

# Run pytest with coverage
try {
    pytest tests/ -v --cov=src --cov-report=term-missing

    $exitCode = $LASTEXITCODE

    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "All tests passed!" -ForegroundColor Green
    } else {
        Write-Host "Some tests failed. Please review the output above." -ForegroundColor Red
    }

    exit $exitCode
}
catch {
    Write-Host "Error running tests: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you have installed dependencies:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}
