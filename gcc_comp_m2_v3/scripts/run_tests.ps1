# Run tests with pytest
# Sets up environment for offline testing (no Vault/external services required)

Write-Host "Running L3 M2.3 Test Suite..." -ForegroundColor Green

# Set PYTHONPATH to project root
$env:PYTHONPATH = $PWD

# Force offline mode for tests
$env:VAULT_ENABLED = "false"
$env:OFFLINE = "true"

Write-Host "Test Configuration:" -ForegroundColor Yellow
Write-Host "  VAULT_ENABLED = $env:VAULT_ENABLED"
Write-Host "  OFFLINE = $env:OFFLINE"
Write-Host ""

# Run pytest with verbose output
Write-Host "Executing pytest..." -ForegroundColor Cyan
pytest -v tests/

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll tests passed! ✓" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed ✗" -ForegroundColor Red
    exit $LASTEXITCODE
}
