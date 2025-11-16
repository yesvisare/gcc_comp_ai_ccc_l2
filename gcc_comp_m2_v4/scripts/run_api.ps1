# Start API server with environment setup
# SERVICES: OPENAI (primary LLM) + PINECONE (vector database)

Write-Host "Starting L3 M2.4 Security Testing API..." -ForegroundColor Green

# Set PYTHONPATH to include project root
$env:PYTHONPATH = $PWD

# Enable services (set to "True" if you have API keys configured)
$env:OPENAI_ENABLED = "False"
$env:PINECONE_ENABLED = "False"

# Optional: Enable services if you have keys
# $env:OPENAI_ENABLED = "True"
# $env:PINECONE_ENABLED = "True"

Write-Host "Service Configuration:" -ForegroundColor Cyan
Write-Host "  OPENAI_ENABLED: $env:OPENAI_ENABLED" -ForegroundColor Yellow
Write-Host "  PINECONE_ENABLED: $env:PINECONE_ENABLED" -ForegroundColor Yellow
Write-Host ""
Write-Host "Starting uvicorn server on http://0.0.0.0:8000" -ForegroundColor Cyan
Write-Host "API docs available at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Start uvicorn with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
