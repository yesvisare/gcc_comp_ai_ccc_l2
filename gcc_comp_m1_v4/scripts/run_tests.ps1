# Run tests for L3 M1.4: Compliance Documentation & Evidence
# Windows PowerShell script

Write-Host "Running tests for L3 M1.4: Compliance Documentation & Evidence..." -ForegroundColor Cyan
Write-Host ""

# Set Python path to include project root
$env:PYTHONPATH = $PWD

# Run pytest with verbose output
Write-Host "Executing pytest..." -ForegroundColor Yellow
pytest tests/ -v --tb=short

Write-Host ""
Write-Host "Tests completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To run with coverage:" -ForegroundColor Yellow
Write-Host "  pytest tests/ --cov=src --cov-report=html" -ForegroundColor Gray
Write-Host ""
Write-Host "To run specific test:" -ForegroundColor Yellow
Write-Host "  pytest tests/test_m1_compliance_foundations_rag_systems.py::TestAuditTrail::test_log_event" -ForegroundColor Gray
