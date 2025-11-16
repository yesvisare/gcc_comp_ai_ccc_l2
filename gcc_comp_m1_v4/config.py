"""
Configuration management for L3 M1.4: Compliance Documentation & Evidence

Handles environment variables and infrastructure service configuration
(PostgreSQL, AWS S3). No external AI services required.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Module configuration
MODULE_NAME = "L3_M1_Compliance_Foundations_RAG_Systems"
VERSION = "1.0.0"

# PostgreSQL configuration (for immutable audit logs)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "compliance_audit")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# AWS S3 configuration (for evidence storage with Object Lock)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "compliance-evidence-bucket")

# Compliance settings
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "2555"))  # ~7 years for SOX 404
EVIDENCE_EXPORT_SCHEDULE = os.getenv("EVIDENCE_EXPORT_SCHEDULE", "daily")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Service status flags
POSTGRES_ENABLED = bool(POSTGRES_PASSWORD)  # Requires password to be enabled
S3_ENABLED = bool(AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)


def get_postgres_connection_string() -> Optional[str]:
    """
    Get PostgreSQL connection string.

    Returns:
        Connection string in format: postgresql://user:password@host:port/database
        Returns None if credentials not configured
    """
    if not POSTGRES_ENABLED:
        logger.warning("⚠️ PostgreSQL credentials not configured")
        return None

    connection_string = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    return connection_string


def get_s3_config() -> Optional[Dict[str, str]]:
    """
    Get AWS S3 configuration.

    Returns:
        Dictionary with S3 configuration:
        - access_key_id: AWS access key
        - secret_access_key: AWS secret key
        - region: AWS region
        - bucket_name: S3 bucket name
        Returns None if credentials not configured
    """
    if not S3_ENABLED:
        logger.warning("⚠️ AWS S3 credentials not configured")
        return None

    return {
        "access_key_id": AWS_ACCESS_KEY_ID,
        "secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region": AWS_REGION,
        "bucket_name": S3_BUCKET_NAME
    }


def get_config() -> Dict[str, Any]:
    """
    Get current configuration.

    Returns:
        Dictionary containing all configuration values (excluding sensitive data)
    """
    config = {
        "module_name": MODULE_NAME,
        "version": VERSION,
        "postgres": {
            "enabled": POSTGRES_ENABLED,
            "host": POSTGRES_HOST,
            "port": POSTGRES_PORT,
            "database": POSTGRES_DB,
            "user": POSTGRES_USER
        },
        "s3": {
            "enabled": S3_ENABLED,
            "region": AWS_REGION,
            "bucket": S3_BUCKET_NAME
        },
        "compliance": {
            "audit_retention_days": AUDIT_RETENTION_DAYS,
            "evidence_export_schedule": EVIDENCE_EXPORT_SCHEDULE
        },
        "log_level": LOG_LEVEL
    }

    logger.info(f"Configuration loaded: Module={MODULE_NAME}, Version={VERSION}")
    return config


def validate_config() -> bool:
    """
    Validate configuration.

    Checks if required infrastructure services are configured.
    The module can run in offline/testing mode without infrastructure.

    Returns:
        True if configuration is valid (even if services disabled), False on error
    """
    warnings = []

    # Check PostgreSQL
    if not POSTGRES_ENABLED:
        warnings.append("PostgreSQL credentials not configured - using in-memory audit trail")

    # Check AWS S3
    if not S3_ENABLED:
        warnings.append("AWS S3 credentials not configured - evidence export disabled")

    # Log warnings
    if warnings:
        logger.warning("⚠️ Running in offline mode:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
        logger.warning("  This is acceptable for development/testing but NOT for production")
    else:
        logger.info("✅ All infrastructure services configured")

    return True


def get_audit_trail_connection():
    """
    Get AuditTrail connection (PostgreSQL or in-memory).

    Returns:
        PostgreSQL connection string if configured, None for in-memory mode
    """
    if POSTGRES_ENABLED:
        return get_postgres_connection_string()

    logger.warning("⚠️ Using in-memory audit trail (not production-ready)")
    return None
