# Run tests for L3 M4.2: Vendor Risk Assessment
# Windows PowerShell script

Write-Host "Running Vendor Risk Assessment Tests..." -ForegroundColor Green
Write-Host ""

# Set Python path to current directory
$env:PYTHONPATH = $PWD

# Run pytest with verbose output
pytest -v tests/

Write-Host ""
Write-Host "Test run complete!" -ForegroundColor Green
