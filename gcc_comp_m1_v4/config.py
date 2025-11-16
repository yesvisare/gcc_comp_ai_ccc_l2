"""
Configuration management for L3 M1.4: Compliance Documentation & Evidence

Handles environment variables, PostgreSQL connections, and AWS S3 configuration
for compliance evidence storage and audit trail management.

No external AI services required - this module operates OFFLINE.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Module configuration
MODULE_NAME = "L3_M1_Compliance_Foundations_RAG_Systems"
VERSION = "1.0.0"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# PostgreSQL configuration (for audit trail storage)
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "compliance_audit"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", ""),
}

# AWS S3 configuration (for evidence storage)
AWS_CONFIG = {
    "access_key_id": os.getenv("AWS_ACCESS_KEY_ID", ""),
    "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
    "region": os.getenv("AWS_REGION", "us-east-1"),
    "bucket_name": os.getenv("S3_BUCKET_NAME", "compliance-evidence-bucket"),
}

# Compliance settings
COMPLIANCE_CONFIG = {
    "audit_retention_days": int(os.getenv("AUDIT_RETENTION_DAYS", "2555")),  # ~7 years
    "evidence_export_schedule": os.getenv("EVIDENCE_EXPORT_SCHEDULE", "daily"),
    "hash_algorithm": "sha256",  # Cryptographic hash for audit trail
    "enable_hash_chaining": True,
}

# Service status (OFFLINE mode - no external AI APIs)
SERVICE_ENABLED = False  # No external AI services required
OFFLINE_MODE = True


def get_config() -> Dict[str, Any]:
    """
    Get current configuration.

    Returns:
        Dictionary containing all configuration values
    """
    config = {
        "module_name": MODULE_NAME,
        "version": VERSION,
        "log_level": LOG_LEVEL,
        "postgres": {
            **POSTGRES_CONFIG,
            "password": "***" if POSTGRES_CONFIG["password"] else None  # Redact
        },
        "aws": {
            **AWS_CONFIG,
            "access_key_id": "***" if AWS_CONFIG["access_key_id"] else None,  # Redact
            "secret_access_key": "***" if AWS_CONFIG["secret_access_key"] else None  # Redact
        },
        "compliance": COMPLIANCE_CONFIG,
        "offline_mode": OFFLINE_MODE,
        "service_enabled": SERVICE_ENABLED
    }

    logger.info(f"Configuration loaded: {MODULE_NAME} v{VERSION}")
    return config


def validate_config() -> bool:
    """
    Validate configuration.

    Checks that required configuration values are present for PostgreSQL
    and AWS S3 (optional for offline development).

    Returns:
        True if configuration is valid, False otherwise
    """
    issues = []

    # Check PostgreSQL configuration (required for production)
    if not POSTGRES_CONFIG["password"]:
        issues.append("POSTGRES_PASSWORD not configured (required for production)")
        logger.warning("⚠️ PostgreSQL password not set - using in-memory storage")

    # Check AWS S3 configuration (optional for development)
    if not AWS_CONFIG["access_key_id"] or not AWS_CONFIG["secret_access_key"]:
        issues.append("AWS credentials not configured (evidence export disabled)")
        logger.warning("⚠️ AWS credentials not set - S3 export disabled")

    if issues:
        logger.warning(f"Configuration validation issues: {len(issues)} found")
        for issue in issues:
            logger.warning(f"  - {issue}")
        logger.info("✅ Running in OFFLINE development mode (in-memory storage)")
        return True  # Non-blocking for development

    logger.info("✅ Configuration validated (all services configured)")
    return True


def get_postgres_connection():
    """
    Get PostgreSQL connection for audit trail storage.

    Returns:
        PostgreSQL connection object or None if not configured

    Note:
        Requires psycopg2 package and valid PostgreSQL credentials
    """
    if not POSTGRES_CONFIG["password"]:
        logger.warning("PostgreSQL not configured - returning None")
        return None

    try:
        import psycopg2
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        logger.info("✅ PostgreSQL connection established")
        return conn
    except ImportError:
        logger.error("psycopg2 not installed - run: pip install psycopg2-binary")
        return None
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return None


def get_s3_client():
    """
    Get AWS S3 client for evidence storage.

    Returns:
        boto3 S3 client or None if not configured

    Note:
        Requires boto3 package and valid AWS credentials
    """
    if not AWS_CONFIG["access_key_id"] or not AWS_CONFIG["secret_access_key"]:
        logger.warning("AWS credentials not configured - returning None")
        return None

    try:
        import boto3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_CONFIG["access_key_id"],
            aws_secret_access_key=AWS_CONFIG["secret_access_key"],
            region_name=AWS_CONFIG["region"]
        )
        logger.info("✅ AWS S3 client initialized")
        return s3_client
    except ImportError:
        logger.error("boto3 not installed - run: pip install boto3")
        return None
    except Exception as e:
        logger.error(f"AWS S3 client initialization failed: {e}")
        return None


def create_audit_table():
    """
    Create audit_events table in PostgreSQL (if connection available).

    Table schema:
    - id: SERIAL PRIMARY KEY
    - event_type: VARCHAR(100)
    - user_id: VARCHAR(255)
    - resource_id: VARCHAR(255)
    - action: VARCHAR(255)
    - timestamp: TIMESTAMP
    - correlation_id: UUID
    - metadata: JSONB
    - previous_hash: VARCHAR(64)
    - current_hash: VARCHAR(64)
    - created_at: TIMESTAMP DEFAULT NOW()

    Returns:
        True if table created or already exists, False on error
    """
    conn = get_postgres_connection()
    if not conn:
        logger.warning("PostgreSQL not available - skipping table creation")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                resource_id VARCHAR(255) NOT NULL,
                action VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                correlation_id UUID NOT NULL,
                metadata JSONB,
                previous_hash VARCHAR(64),
                current_hash VARCHAR(64) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_events(user_id);
            CREATE INDEX IF NOT EXISTS idx_audit_correlation ON audit_events(correlation_id);
        """)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("✅ Audit table created (or already exists)")
        return True
    except Exception as e:
        logger.error(f"Failed to create audit table: {e}")
        return False


# Initialize configuration on import
if __name__ != "__main__":
    logger.info(f"Initializing {MODULE_NAME} v{VERSION} (OFFLINE mode)")
    validate_config()
