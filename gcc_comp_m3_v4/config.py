"""
Configuration management for L3 M3.4: Incident Response & Breach Notification

Loads environment variables and configures logging.
No external service dependencies - all processing is local.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Environment configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Multi-tenant configuration
DEFAULT_TENANT_ID = os.getenv("DEFAULT_TENANT_ID", "tenant-default")

# Notification configuration
NOTIFICATION_EMAIL_FROM = os.getenv("NOTIFICATION_EMAIL_FROM", "compliance@example.com")
DPA_EMAIL = os.getenv("DPA_EMAIL", "dpa@example.com")  # Data Protection Authority

# GDPR configuration
GDPR_NOTIFICATION_HOURS = int(os.getenv("GDPR_NOTIFICATION_HOURS", "72"))

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_config() -> dict:
    """
    Get current configuration settings.

    Returns:
        Dict containing all configuration values
    """
    return {
        "log_level": LOG_LEVEL,
        "environment": ENVIRONMENT,
        "default_tenant_id": DEFAULT_TENANT_ID,
        "notification_email_from": NOTIFICATION_EMAIL_FROM,
        "dpa_email": DPA_EMAIL,
        "gdpr_notification_hours": GDPR_NOTIFICATION_HOURS
    }


# No external clients needed - all processing is local
CLIENTS = {}

logger.info(f"Configuration loaded: environment={ENVIRONMENT}, log_level={LOG_LEVEL}")
