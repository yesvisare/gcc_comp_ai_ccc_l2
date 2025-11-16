# Run test suite for L3 M1.3: Regulatory Frameworks Deep Dive

Write-Host "Running L3 M1.3 Test Suite..." -ForegroundColor Green

# Set environment variables
$env:PYTHONPATH = $PWD

# Run pytest with coverage
Write-Host "`nExecuting pytest with coverage reporting..." -ForegroundColor Yellow
pytest -v tests/ --cov=src --cov-report=term-missing --cov-report=html

Write-Host "`nTest suite complete!" -ForegroundColor Green
Write-Host "Coverage report available in: htmlcov/index.html" -ForegroundColor Cyan
