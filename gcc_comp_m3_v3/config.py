"""
Configuration for L3 M3.3: Audit Logging & SIEM Integration
Handles environment variables and settings.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def get_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.

    This module supports multiple deployment modes:
    - OFFLINE: Local PostgreSQL only (no cloud dependencies)
    - AWS: PostgreSQL + S3 archival
    - SIEM: PostgreSQL + SIEM integration (Splunk/ELK/Datadog)
    - HYBRID: All features enabled

    Returns:
        Dict with configuration settings
    """
    config = {
        # Database configuration (required)
        "db_host": os.getenv("DB_HOST", "localhost"),
        "db_port": int(os.getenv("DB_PORT", "5432")),
        "db_name": os.getenv("DB_NAME", "audit_logs"),
        "db_user": os.getenv("DB_USER", "audit_user"),
        "db_password": os.getenv("DB_PASSWORD", ""),

        # Logging configuration
        "log_file_path": os.getenv("LOG_FILE_PATH", "/var/log/rag/audit.log"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),

        # Immutability strategy
        "immutability_mode": os.getenv("IMMUTABILITY_MODE", "postgresql"),
        "enable_hash_chain": os.getenv("ENABLE_HASH_CHAIN", "true").lower() == "true",

        # AWS S3 configuration (optional)
        "aws_enabled": os.getenv("AWS_ENABLED", "false").lower() == "true",
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", ""),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "s3_bucket_name": os.getenv("S3_BUCKET_NAME", ""),
        "s3_retention_days": int(os.getenv("S3_RETENTION_DAYS", "2555")),  # 7 years

        # SIEM configuration (optional)
        "siem_enabled": os.getenv("SIEM_ENABLED", "false").lower() == "true",
        "siem_platform": os.getenv("SIEM_PLATFORM", "splunk"),

        # Splunk configuration
        "splunk_hec_url": os.getenv("SPLUNK_HEC_URL", ""),
        "splunk_hec_token": os.getenv("SPLUNK_HEC_TOKEN", ""),

        # Elasticsearch configuration
        "elasticsearch_url": os.getenv("ELASTICSEARCH_URL", ""),
        "elasticsearch_index": os.getenv("ELASTICSEARCH_INDEX", "audit-logs"),
        "elasticsearch_api_key": os.getenv("ELASTICSEARCH_API_KEY", ""),

        # Datadog configuration
        "datadog_api_key": os.getenv("DATADOG_API_KEY", ""),
        "datadog_app_key": os.getenv("DATADOG_APP_KEY", ""),
        "datadog_site": os.getenv("DATADOG_SITE", "datadoghq.com"),

        # Multi-tenant configuration
        "tenant_id": os.getenv("TENANT_ID", "default_tenant"),
        "enable_multi_tenant": os.getenv("ENABLE_MULTI_TENANT", "false").lower() == "true",

        # Retention policy
        "hot_storage_days": int(os.getenv("HOT_STORAGE_DAYS", "90")),
        "warm_storage_days": int(os.getenv("WARM_STORAGE_DAYS", "365")),
        "cold_storage_days": int(os.getenv("COLD_STORAGE_DAYS", "2555")),
    }

    # Validate required configuration
    if not config["db_password"]:
        logger.warning("⚠️ DB_PASSWORD not set - database connection may fail")

    # Validate AWS configuration if enabled
    if config["aws_enabled"]:
        if not config["aws_access_key_id"] or not config["aws_secret_access_key"]:
            logger.warning("⚠️ AWS enabled but credentials not set")
        if not config["s3_bucket_name"]:
            logger.warning("⚠️ AWS enabled but S3_BUCKET_NAME not set")

    # Validate SIEM configuration if enabled
    if config["siem_enabled"]:
        platform = config["siem_platform"]
        if platform == "splunk" and not config["splunk_hec_token"]:
            logger.warning("⚠️ Splunk SIEM enabled but SPLUNK_HEC_TOKEN not set")
        elif platform == "elasticsearch" and not config["elasticsearch_api_key"]:
            logger.warning("⚠️ Elasticsearch SIEM enabled but ELASTICSEARCH_API_KEY not set")
        elif platform == "datadog" and not config["datadog_api_key"]:
            logger.warning("⚠️ Datadog SIEM enabled but DATADOG_API_KEY not set")

    logger.info(f"Configuration loaded - Mode: {config['immutability_mode']}, "
                f"AWS: {config['aws_enabled']}, SIEM: {config['siem_enabled']}")

    return config


def get_db_connection_string(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Build PostgreSQL connection string from configuration.

    Args:
        config: Configuration dictionary (if None, will load from get_config())

    Returns:
        PostgreSQL connection string
    """
    if config is None:
        config = get_config()

    return (
        f"host={config['db_host']} "
        f"port={config['db_port']} "
        f"dbname={config['db_name']} "
        f"user={config['db_user']} "
        f"password={config['db_password']}"
    )


def validate_configuration() -> bool:
    """
    Validate that all required configuration is present.

    Returns:
        True if configuration is valid, False otherwise
    """
    config = get_config()

    # Check required database configuration
    required_fields = ["db_host", "db_port", "db_name", "db_user", "db_password"]
    for field in required_fields:
        if not config.get(field):
            logger.error(f"❌ Required configuration missing: {field}")
            return False

    logger.info("✅ Configuration validation passed")
    return True
