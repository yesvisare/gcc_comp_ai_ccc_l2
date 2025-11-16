# ============================================================================
# L3 M1.2: Data Governance Requirements for RAG - Test Runner
# ============================================================================
# This script runs the pytest test suite for the data governance system.
# It tests all 6 components plus integration tests.
#
# Usage: .\scripts\run_tests.ps1
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "L3 M1.2: Data Governance Requirements for RAG - Test Suite" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to project root
$env:PYTHONPATH = $PWD
Write-Host "[INFO] PYTHONPATH set to: $PWD" -ForegroundColor Green
Write-Host ""

# Run pytest with quiet mode
Write-Host "[INFO] Running test suite..." -ForegroundColor Yellow
Write-Host ""

# Run tests with minimal output
pytest -q tests/

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Optional: Run with verbose output and coverage
# Uncomment the line below for detailed test output
# pytest -v --cov=src tests/

# Optional: Run specific test categories
# pytest tests/ -k "test_classification"  # Only classification tests
# pytest tests/ -k "test_gdpr"           # Only GDPR tests
