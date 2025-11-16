# Run tests for L3 M2.2: Authorization & Multi-Tenant Access Control
# Windows PowerShell script

Write-Host "Running tests for L3 M2.2: Authorization & Multi-Tenant Access Control" -ForegroundColor Green
Write-Host ""

# Set Python path
$env:PYTHONPATH = $PWD

# Set test environment variables (offline mode)
$env:PINECONE_ENABLED = "false"
$env:POSTGRES_ENABLED = "false"
$env:OPA_ENABLED = "false"

Write-Host "Test Configuration:" -ForegroundColor Cyan
Write-Host "  Running in offline mode (mocked services)" -ForegroundColor Gray
Write-Host ""

# Run pytest with verbose output
Write-Host "Executing pytest..." -ForegroundColor Yellow
Write-Host ""

pytest -v tests/

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Some tests failed. Please review the output above." -ForegroundColor Red
    exit $LASTEXITCODE
}
