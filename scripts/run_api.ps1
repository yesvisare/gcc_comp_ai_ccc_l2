# ============================================================================
# L3 M1.2: Data Governance Requirements for RAG - API Server Launcher
# ============================================================================
# This script starts the FastAPI server for the data governance system.
# It sets up environment variables and launches uvicorn with hot reload.
#
# Usage: .\scripts\run_api.ps1
# ============================================================================

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "L3 M1.2: Data Governance Requirements for RAG - API Server" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to project root
$env:PYTHONPATH = $PWD
Write-Host "[INFO] PYTHONPATH set to: $PWD" -ForegroundColor Green

# Optional: Enable services (set to "True" to enable)
# Presidio runs locally (no API key needed, but requires spaCy model)
$env:PRESIDIO_ENABLED = "True"
Write-Host "[INFO] PRESIDIO_ENABLED = True (local PII detection)" -ForegroundColor Green

# OpenAI (optional - for embeddings)
# Uncomment and set API key in .env if you want to enable OpenAI
# $env:OPENAI_ENABLED = "True"

# Pinecone (optional - for vector database)
# Uncomment and set API key in .env if you want to enable Pinecone
# $env:PINECONE_ENABLED = "True"

Write-Host ""
Write-Host "[INFO] Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "[INFO] API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "[INFO] Health Check: http://localhost:8000/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Magenta
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# Start uvicorn with hot reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
