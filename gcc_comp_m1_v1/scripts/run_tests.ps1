# PowerShell script to run tests
# L3 M1.1: Why Compliance Matters in GCC RAG Systems

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M1.1 Compliance Risk Assessment Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to project root
$env:PYTHONPATH = $PWD.Path
Write-Host "✓ PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Green
Write-Host ""

# Check if pytest is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    $pytestVersion = pytest --version 2>&1
    Write-Host "✓ pytest found: $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ pytest not found. Install with: pip install pytest" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host ""

# Run pytest with verbose output
pytest tests/ -v --tb=short

# Capture exit code
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "To run specific tests:" -ForegroundColor Yellow
Write-Host "  pytest tests/test_m1_compliance_foundations_rag_systems.py::TestDataClassifier -v" -ForegroundColor Gray
Write-Host ""
Write-Host "To run with coverage:" -ForegroundColor Yellow
Write-Host "  pytest tests/ --cov=src --cov-report=html" -ForegroundColor Gray
Write-Host ""

exit $exitCode
