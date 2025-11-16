"""
Configuration management for L3 M2.2: Authorization & Multi-Tenant Access Control

Handles initialization of:
- Pinecone vector database client
- PostgreSQL database connection
- Open Policy Agent (OPA) client
- JWT configuration
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Pinecone Configuration
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "gcc-compliance-m2")

# PostgreSQL Configuration
POSTGRES_ENABLED = os.getenv("POSTGRES_ENABLED", "false").lower() == "true"
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "gcc_auth")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# OPA Configuration
OPA_ENABLED = os.getenv("OPA_ENABLED", "false").lower() == "true"
OPA_URL = os.getenv("OPA_URL", "http://localhost:8181")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))

# Application Settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
AUDIT_LOG_RETENTION_DAYS = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "2555"))  # 7 years


def get_pinecone_client():
    """
    Initialize Pinecone client if enabled.

    Returns:
        Pinecone client instance or None if disabled/unavailable
    """
    if not PINECONE_ENABLED:
        logger.warning("⚠️ PINECONE disabled - using offline mode")
        return None

    if not PINECONE_API_KEY:
        logger.warning("⚠️ PINECONE_API_KEY not set")
        return None

    try:
        import pinecone
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT
        )
        logger.info(f"✅ Pinecone client initialized (environment: {PINECONE_ENVIRONMENT})")
        return pinecone
    except ImportError:
        logger.error("❌ pinecone-client package not installed")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Pinecone: {e}")
        return None


def get_postgres_connection_string() -> Optional[str]:
    """
    Build PostgreSQL connection string.

    Returns:
        Connection string or None if disabled
    """
    if not POSTGRES_ENABLED:
        logger.warning("⚠️ PostgreSQL disabled - using in-memory storage")
        return None

    if not POSTGRES_PASSWORD:
        logger.warning("⚠️ POSTGRES_PASSWORD not set")
        return None

    conn_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    logger.info(f"✅ PostgreSQL connection configured (host: {POSTGRES_HOST})")
    return conn_string


def get_database_engine():
    """
    Initialize SQLAlchemy database engine.

    Returns:
        SQLAlchemy engine or None if disabled
    """
    conn_string = get_postgres_connection_string()
    if not conn_string:
        return None

    try:
        from sqlalchemy import create_engine
        engine = create_engine(conn_string, echo=False)
        logger.info("✅ Database engine initialized")
        return engine
    except ImportError:
        logger.error("❌ sqlalchemy package not installed")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {e}")
        return None


def get_opa_client():
    """
    Initialize OPA (Open Policy Agent) client.

    Returns:
        OPA client configuration or None if disabled
    """
    if not OPA_ENABLED:
        logger.warning("⚠️ OPA disabled - using basic RBAC only")
        return None

    try:
        import requests
        # Test OPA connection
        response = requests.get(f"{OPA_URL}/health", timeout=2)
        if response.status_code == 200:
            logger.info(f"✅ OPA client initialized (url: {OPA_URL})")
            return {"url": OPA_URL, "client": requests}
        else:
            logger.warning(f"⚠️ OPA health check failed: {response.status_code}")
            return None
    except ImportError:
        logger.error("❌ requests package not installed")
        return None
    except Exception as e:
        logger.warning(f"⚠️ OPA not available: {e}")
        return None


# Initialize clients
pinecone_client = get_pinecone_client()
db_engine = get_database_engine()
opa_client = get_opa_client()


# Role definitions
class Role:
    """User role definitions for RBAC."""
    ADMIN = "admin"
    ANALYST = "analyst"
    COMPLIANCE_OFFICER = "compliance_officer"


# Permission definitions
class Permission:
    """Permission definitions for RBAC."""
    # Namespace management
    CREATE_NAMESPACE = "create_namespace"
    DELETE_NAMESPACE = "delete_namespace"

    # User management
    ASSIGN_USER_TO_NAMESPACE = "assign_user_to_namespace"
    MANAGE_USERS = "manage_users"

    # Query operations
    QUERY_OWN_NAMESPACE = "query_own_namespace"
    QUERY_ALL_NAMESPACES = "query_all_namespaces"

    # Policy management
    MANAGE_POLICIES = "manage_policies"

    # Audit operations
    VIEW_AUDIT_LOGS = "view_audit_logs"
    EXPORT_AUDIT_LOGS = "export_audit_logs"


# Role-Permission Mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.CREATE_NAMESPACE,
        Permission.DELETE_NAMESPACE,
        Permission.ASSIGN_USER_TO_NAMESPACE,
        Permission.MANAGE_USERS,
        Permission.QUERY_OWN_NAMESPACE,
        Permission.QUERY_ALL_NAMESPACES,
        Permission.MANAGE_POLICIES,
        Permission.VIEW_AUDIT_LOGS,
        Permission.EXPORT_AUDIT_LOGS,
    ],
    Role.ANALYST: [
        Permission.QUERY_OWN_NAMESPACE,
    ],
    Role.COMPLIANCE_OFFICER: [
        Permission.QUERY_ALL_NAMESPACES,
        Permission.VIEW_AUDIT_LOGS,
        Permission.EXPORT_AUDIT_LOGS,
    ],
}


def has_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if a role has a specific permission.

    Args:
        user_role: User's role (admin, analyst, compliance_officer)
        required_permission: Required permission

    Returns:
        True if role has permission, False otherwise
    """
    role_perms = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in role_perms
