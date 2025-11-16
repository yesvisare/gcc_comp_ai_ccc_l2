"""
Configuration management for L3 M2.3: Encryption & Secrets Management

Loads environment variables and initializes Vault client for dynamic secrets retrieval.
SERVICE: HashiCorp Vault (primary), with OpenAI/Pinecone credentials managed by Vault
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Vault Configuration (Primary Service)
VAULT_ENABLED = os.getenv("VAULT_ENABLED", "false").lower() == "true"
VAULT_ADDR = os.getenv("VAULT_ADDR", "http://localhost:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
VAULT_NAMESPACE = os.getenv("VAULT_NAMESPACE", "gcc-secrets")

# Kubernetes ServiceAccount Auth (Production)
VAULT_K8S_ROLE = os.getenv("VAULT_K8S_ROLE", "rag-api")
VAULT_K8S_SA_TOKEN_PATH = os.getenv(
    "VAULT_K8S_SA_TOKEN_PATH",
    "/var/run/secrets/kubernetes.io/serviceaccount/token"
)

# Secondary Services (fallback when Vault disabled)
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")

# PostgreSQL (fallback when Vault disabled)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "gcc_rag")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# TLS Configuration
TLS_ENABLED = os.getenv("TLS_ENABLED", "false").lower() == "true"
CERT_PATH = os.getenv("CERT_PATH", "/etc/tls/certs")
CERT_RENEWAL_DAYS = int(os.getenv("CERT_RENEWAL_DAYS", "30"))

# Offline Mode
OFFLINE = os.getenv("OFFLINE", "false").lower() == "true"


def init_vault_client() -> Optional[Any]:
    """
    Initialize HashiCorp Vault client with Kubernetes ServiceAccount auth.

    Returns:
        hvac.Client instance if Vault enabled and authenticated, None otherwise
    """
    if not VAULT_ENABLED:
        logger.warning("⚠️ VAULT_ENABLED=false - skipping Vault client initialization")
        return None

    try:
        import hvac

        client = hvac.Client(url=VAULT_ADDR)

        # Attempt Kubernetes ServiceAccount authentication (production)
        if os.path.exists(VAULT_K8S_SA_TOKEN_PATH):
            logger.info("Authenticating to Vault via Kubernetes ServiceAccount")
            with open(VAULT_K8S_SA_TOKEN_PATH, 'r') as f:
                jwt_token = f.read().strip()

            auth_response = client.auth.kubernetes.login(
                role=VAULT_K8S_ROLE,
                jwt=jwt_token
            )
            client.token = auth_response['auth']['client_token']
            logger.info("✓ Vault authenticated via K8s ServiceAccount")

        # Fallback to static token (development only)
        elif VAULT_TOKEN:
            logger.warning("Using static VAULT_TOKEN for authentication (dev mode)")
            client.token = VAULT_TOKEN

        else:
            logger.error("❌ No Vault authentication method available")
            return None

        # Verify authentication
        if not client.is_authenticated():
            logger.error("❌ Vault authentication failed")
            return None

        logger.info(f"✓ Vault client initialized: {VAULT_ADDR}")
        return client

    except ImportError:
        logger.error("❌ hvac library not installed: pip install hvac")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Vault client: {e}")
        return None


def init_secondary_clients() -> Dict[str, Any]:
    """
    Initialize secondary service clients (OpenAI, Pinecone).

    In production, credentials are retrieved from Vault.
    In development/offline mode, uses environment variables directly.

    Returns:
        Dict containing initialized clients or empty dict if disabled
    """
    clients = {}

    if OFFLINE:
        logger.warning("⚠️ OFFLINE=true - skipping all external service clients")
        return clients

    # OpenAI Client
    if OPENAI_ENABLED and OPENAI_API_KEY:
        try:
            from openai import OpenAI
            clients["openai"] = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("✓ OpenAI client initialized")
        except ImportError:
            logger.warning("⚠️ openai library not installed")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI client: {e}")

    # Pinecone Client
    if PINECONE_ENABLED and PINECONE_API_KEY:
        try:
            from pinecone import Pinecone
            clients["pinecone"] = Pinecone(api_key=PINECONE_API_KEY)
            logger.info("✓ Pinecone client initialized")
        except ImportError:
            logger.warning("⚠️ pinecone-client library not installed")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pinecone client: {e}")

    return clients


# Global client instances
VAULT_CLIENT = init_vault_client()
SECONDARY_CLIENTS = init_secondary_clients()
