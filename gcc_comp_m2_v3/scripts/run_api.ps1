# Start API server with environment setup
# SERVICE: HashiCorp Vault (primary) with OpenAI/Pinecone credential management

Write-Host "Starting L3 M2.3 API Server..." -ForegroundColor Green

# Set PYTHONPATH to project root
$env:PYTHONPATH = $PWD

# Vault configuration (adjust for your environment)
$env:VAULT_ENABLED = "False"  # Set to "True" if Vault is available
$env:VAULT_ADDR = "http://localhost:8200"
# $env:VAULT_TOKEN = "dev-root-token-uuid"  # Uncomment for dev mode

# Secondary services (fallback when Vault disabled)
$env:OPENAI_ENABLED = "False"
$env:PINECONE_ENABLED = "False"

# Offline mode for development
$env:OFFLINE = "False"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  VAULT_ENABLED = $env:VAULT_ENABLED"
Write-Host "  OPENAI_ENABLED = $env:OPENAI_ENABLED"
Write-Host "  OFFLINE = $env:OFFLINE"
Write-Host ""

Write-Host "Starting uvicorn server on http://0.0.0.0:8000 ..." -ForegroundColor Cyan
uvicorn app:app --reload --host 0.0.0.0 --port 8000
