# Start FastAPI server for L3 M4.1: Model Cards & AI Governance
# SERVICE: LOCAL (No external AI APIs required)

Write-Host "Starting L3 M4.1 AI Governance API..." -ForegroundColor Cyan
Write-Host ""

# Set Python path to include project root
$env:PYTHONPATH = $PWD.Path

# Optional: Enable PostgreSQL or JIRA integrations
# Uncomment and configure if you want enterprise integrations
# $env:POSTGRES_ENABLED = "True"
# $env:POSTGRES_URL = "postgresql://user:password@localhost:5432/governance_db"
# $env:JIRA_ENABLED = "True"
# $env:JIRA_URL = "https://your-company.atlassian.net"
# $env:JIRA_TOKEN = "your_jira_token"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - Mode: Local (offline operation)"
Write-Host "  - Python Path: $env:PYTHONPATH"
Write-Host "  - Server: http://localhost:8000"
Write-Host ""
Write-Host "Core governance features work offline - no API keys needed!" -ForegroundColor Green
Write-Host ""

# Start server
Write-Host "Starting uvicorn server..." -ForegroundColor Cyan
uvicorn app:app --reload --host 0.0.0.0 --port 8000
