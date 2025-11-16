# Run tests with pytest
$env:PYTHONPATH = $PWD
$env:LOG_LEVEL = "ERROR"  # Reduce noise during tests

Write-Host "Running L3 M3.4 test suite..." -ForegroundColor Green
Write-Host ""

pytest -v tests/
