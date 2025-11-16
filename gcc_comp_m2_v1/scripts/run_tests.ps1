# PowerShell script to run tests
# L3 M2: Security_Access_Control

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  L3 M2: Security_Access_Control" -ForegroundColor Cyan
Write-Host "  Test Suite Runner" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:PYTHONPATH = $PWD
$env:ENVIRONMENT = "test"

# Check if virtual environment is activated
if (-Not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Warning: Virtual environment not activated" -ForegroundColor Yellow
    Write-Host "   Run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
}

# Parse command line arguments
param(
    [switch]$coverage,
    [switch]$verbose,
    [switch]$html,
    [string]$test
)

# Build pytest command
$pytestCmd = "pytest"
$pytestArgs = @()

# Add test path
if ($test) {
    $pytestArgs += $test
} else {
    $pytestArgs += "tests/"
}

# Add verbosity
if ($verbose) {
    $pytestArgs += "-v"
} else {
    $pytestArgs += "-q"
}

# Add coverage
if ($coverage) {
    $pytestArgs += "--cov=src"
    $pytestArgs += "--cov-report=term-missing"
    Write-Host "Running tests with coverage..." -ForegroundColor Green
} else {
    Write-Host "Running tests..." -ForegroundColor Green
}

# Add HTML coverage report
if ($html) {
    $pytestArgs += "--cov-report=html"
    Write-Host "  • HTML coverage report will be generated" -ForegroundColor White
}

Write-Host ""

# Run pytest
$fullCommand = "$pytestCmd $($pytestArgs -join ' ')"
Write-Host "Command: $fullCommand" -ForegroundColor Gray
Write-Host ""

try {
    & $pytestCmd @pytestArgs
    $exitCode = $LASTEXITCODE

    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "✓ All tests passed!" -ForegroundColor Green
    } else {
        Write-Host "❌ Some tests failed" -ForegroundColor Red
    }

    # Show HTML coverage report location if generated
    if ($html) {
        Write-Host ""
        Write-Host "HTML Coverage Report: htmlcov/index.html" -ForegroundColor Cyan
        Write-Host "Open with: Start-Process htmlcov/index.html" -ForegroundColor Gray
    }

    exit $exitCode
}
catch {
    Write-Host ""
    Write-Host "❌ Error running tests: $_" -ForegroundColor Red
    exit 1
}

# Usage examples:
# .\scripts\run_tests.ps1                    # Run all tests (quiet mode)
# .\scripts\run_tests.ps1 -verbose           # Run with verbose output
# .\scripts\run_tests.ps1 -coverage          # Run with coverage report
# .\scripts\run_tests.ps1 -coverage -html    # Run with HTML coverage report
# .\scripts\run_tests.ps1 -test tests/test_m2_security_access_control.py::TestOAuthClient  # Run specific test
