"""
FastAPI application for L3 M2.3: Encryption & Secrets Management

Provides REST API endpoints for Vault-based secrets retrieval, AES-256 encryption,
TLS certificate management, and key rotation for GCC-compliant RAG systems.

SERVICE: HashiCorp Vault (primary) with OpenAI/Pinecone credential management
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, Optional
import os
from datetime import datetime

from src.l3_m2_security_access_control import (
    VaultClient,
    EncryptionManager,
    TLSCertificateManager,
    KeyRotationManager,
    audit_log_entry
)
from config import VAULT_CLIENT, VAULT_ENABLED, OFFLINE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M2.3: Encryption & Secrets Management API",
    description="HashiCorp Vault integration for dynamic secrets, AES-256 encryption, and automated key rotation",
    version="1.0.0"
)


# Request/Response Models

class SecretRequest(BaseModel):
    """Request model for secret retrieval"""
    secret_path: str = Field(..., description="Path to secret in Vault (e.g., 'gcc-secrets/openai')")


class EncryptRequest(BaseModel):
    """Request model for encryption"""
    plaintext: str = Field(..., description="Data to encrypt")
    kek_b64: Optional[str] = Field(None, description="Base64-encoded KEK (optional, uses default if not provided)")


class DecryptRequest(BaseModel):
    """Request model for decryption"""
    encrypted_b64: str = Field(..., description="Base64-encoded encrypted data")
    kek_b64: Optional[str] = Field(None, description="Base64-encoded KEK (optional, uses default if not provided)")


class KeyRotationRequest(BaseModel):
    """Request model for API key rotation"""
    service: str = Field(..., description="Service name (openai, pinecone)")
    new_key: str = Field(..., description="New API key value")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    module: str
    vault_enabled: bool
    offline_mode: bool
    vault_authenticated: bool


class SecretResponse(BaseModel):
    """Secret retrieval response"""
    secret_data: Dict[str, Any]
    retrieved_at: str


class EncryptResponse(BaseModel):
    """Encryption response"""
    encrypted_data: str


class DecryptResponse(BaseModel):
    """Decryption response"""
    plaintext: str


class CertificateStatusResponse(BaseModel):
    """Certificate status response"""
    days_until_expiry: int
    should_renew: bool
    cert_path: str


# Endpoints

@app.get("/", response_model=HealthResponse)
def root():
    """
    Health check endpoint

    Returns system status and Vault connectivity
    """
    vault_authenticated = False
    if VAULT_CLIENT:
        try:
            vault_authenticated = VAULT_CLIENT.client.is_authenticated()
        except Exception:
            pass

    return HealthResponse(
        status="healthy",
        module="L3_M2_Security_Access_Control",
        vault_enabled=VAULT_ENABLED,
        offline_mode=OFFLINE,
        vault_authenticated=vault_authenticated
    )


@app.post("/secrets/retrieve", response_model=SecretResponse)
def retrieve_secret(request: SecretRequest):
    """
    Retrieve secret from HashiCorp Vault

    Requires VAULT_ENABLED=true in environment.

    Example:
        POST /secrets/retrieve
        {
            "secret_path": "gcc-secrets/openai"
        }

        Response:
        {
            "secret_data": {"api_key": "sk-..."},
            "retrieved_at": "2025-01-15T10:30:00Z"
        }
    """
    if not VAULT_ENABLED or not VAULT_CLIENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not enabled. Set VAULT_ENABLED=true in .env"
        )

    if OFFLINE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Offline mode enabled - cannot retrieve secrets"
        )

    try:
        secret_data = VAULT_CLIENT.get_secret(request.secret_path)

        # Log audit event
        audit_log_entry(
            event_type="secret_retrieval",
            timestamp=datetime.utcnow().isoformat(),
            status="success",
            secret_path=request.secret_path
        )

        return SecretResponse(
            secret_data=secret_data,
            retrieved_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Secret retrieval failed: {e}")
        audit_log_entry(
            event_type="secret_retrieval",
            timestamp=datetime.utcnow().isoformat(),
            status="failed",
            secret_path=request.secret_path,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve secret: {str(e)}"
        )


@app.get("/secrets/openai")
def get_openai_key():
    """
    Retrieve OpenAI API key from Vault

    Convenience endpoint for OpenAI credential retrieval.
    """
    if not VAULT_ENABLED or not VAULT_CLIENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not enabled. Set VAULT_ENABLED=true in .env"
        )

    try:
        api_key = VAULT_CLIENT.get_openai_key()
        return {
            "service": "openai",
            "key_retrieved": True,
            "key_preview": api_key[:10] + "..." if api_key else None
        }
    except Exception as e:
        logger.error(f"OpenAI key retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/secrets/pinecone")
def get_pinecone_key():
    """
    Retrieve Pinecone API key from Vault

    Convenience endpoint for Pinecone credential retrieval.
    """
    if not VAULT_ENABLED or not VAULT_CLIENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not enabled. Set VAULT_ENABLED=true in .env"
        )

    try:
        api_key = VAULT_CLIENT.get_pinecone_key()
        return {
            "service": "pinecone",
            "key_retrieved": True,
            "key_preview": api_key[:10] + "..." if api_key else None
        }
    except Exception as e:
        logger.error(f"Pinecone key retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/encrypt", response_model=EncryptResponse)
def encrypt_data(request: EncryptRequest):
    """
    Encrypt data using AES-256 with envelope encryption

    Uses KEK from Vault if kek_b64 not provided.

    Example:
        POST /encrypt
        {
            "plaintext": "sensitive PII data"
        }

        Response:
        {
            "encrypted_data": "base64_encrypted_string..."
        }
    """
    try:
        # Use provided KEK or default (from environment/Vault)
        if request.kek_b64:
            import base64
            kek = base64.b64decode(request.kek_b64)
        else:
            # In production, retrieve KEK from Vault
            # For demo, use environment variable or generate
            kek = os.urandom(32)  # Demo KEK
            logger.warning("⚠️ Using demo KEK - in production, retrieve from Vault")

        manager = EncryptionManager(kek)
        encrypted = manager.encrypt(request.plaintext)

        return EncryptResponse(encrypted_data=encrypted)

    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption failed: {str(e)}"
        )


@app.post("/decrypt", response_model=DecryptResponse)
def decrypt_data(request: DecryptRequest):
    """
    Decrypt AES-256 encrypted data

    Requires same KEK used for encryption.

    Example:
        POST /decrypt
        {
            "encrypted_b64": "base64_encrypted_string..."
        }

        Response:
        {
            "plaintext": "sensitive PII data"
        }
    """
    try:
        # Use provided KEK or default
        if request.kek_b64:
            import base64
            kek = base64.b64decode(request.kek_b64)
        else:
            kek = os.urandom(32)  # Demo KEK
            logger.warning("⚠️ Using demo KEK - must match encryption KEK")

        manager = EncryptionManager(kek)
        plaintext = manager.decrypt(request.encrypted_b64)

        return DecryptResponse(plaintext=plaintext)

    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decryption failed: {str(e)}"
        )


@app.get("/tls/status", response_model=CertificateStatusResponse)
def check_tls_certificate():
    """
    Check TLS certificate expiration status

    Returns days until expiry and renewal recommendation.
    """
    cert_path = os.getenv("CERT_PATH", "/etc/tls/certs")

    try:
        manager = TLSCertificateManager(cert_path)
        days_left = manager.check_expiry()
        should_renew = manager.should_renew()

        return CertificateStatusResponse(
            days_until_expiry=days_left,
            should_renew=should_renew,
            cert_path=cert_path
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate not found at {cert_path}"
        )
    except Exception as e:
        logger.error(f"Certificate check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/keys/rotate")
def rotate_key(request: KeyRotationRequest):
    """
    Rotate API key in Vault (quarterly schedule)

    Updates Vault secret with new key value and logs audit event.

    Example:
        POST /keys/rotate
        {
            "service": "openai",
            "new_key": "sk-new-key-xyz"
        }
    """
    if not VAULT_ENABLED or not VAULT_CLIENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not enabled. Set VAULT_ENABLED=true in .env"
        )

    try:
        rotation_manager = KeyRotationManager(VAULT_CLIENT)
        rotation_manager.rotate_api_key(request.service, request.new_key)

        return {
            "status": "success",
            "service": request.service,
            "rotated_at": datetime.utcnow().isoformat(),
            "message": f"API key rotated for {request.service}"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Key rotation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key rotation failed: {str(e)}"
        )


@app.post("/keys/rotate-postgres")
def rotate_postgres_credentials():
    """
    Rotate PostgreSQL credentials via Vault database engine

    Generates new time-limited credentials (24-hour TTL).
    """
    if not VAULT_ENABLED or not VAULT_CLIENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not enabled. Set VAULT_ENABLED=true in .env"
        )

    try:
        rotation_manager = KeyRotationManager(VAULT_CLIENT)
        new_creds = rotation_manager.rotate_postgres_credentials()

        # Don't return actual credentials in response
        return {
            "status": "success",
            "rotated_at": datetime.utcnow().isoformat(),
            "message": "PostgreSQL credentials rotated",
            "username": new_creds.get("username", "N/A"),
            "ttl_hours": 24
        }

    except Exception as e:
        logger.error(f"PostgreSQL rotation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PostgreSQL rotation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
