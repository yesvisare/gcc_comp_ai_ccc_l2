# Run Tests for L3 M1.4: Compliance Documentation & Evidence
# Windows PowerShell script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M1.4: Compliance Documentation & Evidence" -ForegroundColor Cyan
Write-Host "Running Test Suite..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to project root
$env:PYTHONPATH = $PWD.Path

# Check if pytest is installed
try {
    $pytestVersion = pytest --version 2>&1
    Write-Host "✅ pytest found: $pytestVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ pytest not found" -ForegroundColor Red
    Write-Host "Installing pytest..." -ForegroundColor Yellow
    pip install pytest pytest-cov
}

Write-Host ""
Write-Host "Test Categories:" -ForegroundColor Green
Write-Host "  - Audit Event Tests" -ForegroundColor Gray
Write-Host "  - Audit Trail & Hash Chain Tests" -ForegroundColor Gray
Write-Host "  - Compliance Report Tests" -ForegroundColor Gray
Write-Host "  - Evidence Collector Tests" -ForegroundColor Gray
Write-Host "  - Vendor Risk Assessment Tests" -ForegroundColor Gray
Write-Host "  - Integration Tests" -ForegroundColor Gray
Write-Host ""

# Run tests with verbose output
Write-Host "Running tests..." -ForegroundColor Green
Write-Host ""

try {
    pytest tests/ -v --tb=short --color=yes

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✅ All tests passed!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "❌ Some tests failed" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
catch {
    Write-Host ""
    Write-Host "❌ Test execution failed" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "To run tests with coverage:" -ForegroundColor Yellow
Write-Host "  pytest --cov=src tests/ --cov-report=html" -ForegroundColor Gray
Write-Host "  Then open: htmlcov/index.html" -ForegroundColor Gray
Write-Host ""

Write-Host "To run specific test:" -ForegroundColor Yellow
Write-Host "  pytest tests/test_m1_compliance_foundations_rag_systems.py::test_name -v" -ForegroundColor Gray
Write-Host ""
