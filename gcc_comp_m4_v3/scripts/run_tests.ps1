# Run pytest test suite for L3 M4.3: Change Management & Compliance

Write-Host "Running Change Management Tests..." -ForegroundColor Green
Write-Host ""

# Set environment variables
$env:PYTHONPATH = $PWD
$env:OFFLINE = "true"
Write-Host "✓ PYTHONPATH set to: $PWD" -ForegroundColor Green
Write-Host "✓ OFFLINE mode enabled for tests" -ForegroundColor Green
Write-Host ""

# Run pytest
pytest -v tests/

Write-Host ""
Write-Host "Test run completed!" -ForegroundColor Green
