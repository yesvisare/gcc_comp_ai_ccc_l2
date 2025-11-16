"""
Configuration management for L3 M4.1: Model Cards & AI Governance

This module is a LOCAL-ONLY implementation with no external AI service dependencies.
Uses standard Python libraries for governance documentation and bias detection.

SERVICE: LOCAL (No external APIs - pandas, scipy, json only)
"""

import os
import logging
from typing import Optional, Any, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# This module runs entirely offline - no external AI services required
# It uses local libraries for:
# - JSON/Markdown model card generation
# - pandas/scipy for statistical bias testing
# - Local logging and audit trails

# Configuration for optional enterprise integrations
POSTGRES_ENABLED = os.getenv("POSTGRES_ENABLED", "false").lower() == "true"
JIRA_ENABLED = os.getenv("JIRA_ENABLED", "false").lower() == "true"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def init_clients() -> Dict[str, Any]:
    """
    Initialize optional enterprise system clients.

    This governance module works fully offline. Optional integrations:
    - PostgreSQL: For persistent audit logging
    - JIRA: For incident tracking

    Returns:
        Dict containing initialized clients or empty dict if disabled
    """
    clients = {}

    # PostgreSQL for audit logging (optional)
    if POSTGRES_ENABLED:
        postgres_url = os.getenv("POSTGRES_URL")
        if postgres_url:
            try:
                # Example: import psycopg2
                # clients["postgres"] = psycopg2.connect(postgres_url)
                logger.info("✓ PostgreSQL client initialized (audit logging enabled)")
            except Exception as e:
                logger.warning(f"⚠️ PostgreSQL connection failed: {e}")
        else:
            logger.warning("⚠️ POSTGRES_URL not found - audit logging will use local files")

    # JIRA for incident tracking (optional)
    if JIRA_ENABLED:
        jira_url = os.getenv("JIRA_URL")
        jira_token = os.getenv("JIRA_TOKEN")
        if jira_url and jira_token:
            try:
                # Example: from jira import JIRA
                # clients["jira"] = JIRA(server=jira_url, token_auth=jira_token)
                logger.info("✓ JIRA client initialized (incident tracking enabled)")
            except Exception as e:
                logger.warning(f"⚠️ JIRA connection failed: {e}")
        else:
            logger.warning("⚠️ JIRA_URL or JIRA_TOKEN not found - incidents will be logged locally")

    if not clients:
        logger.info("ℹ️ Running in standalone mode - no enterprise integrations enabled")
        logger.info("   Model cards, bias detection, and governance workflows work offline")

    return clients


# Global clients dict (empty for local-only operation)
CLIENTS = init_clients()


def get_config() -> Dict[str, Any]:
    """
    Get current configuration settings.

    Returns:
        Dict of all configuration values
    """
    return {
        "log_level": LOG_LEVEL,
        "postgres_enabled": POSTGRES_ENABLED,
        "jira_enabled": JIRA_ENABLED,
        "mode": "offline" if not (POSTGRES_ENABLED or JIRA_ENABLED) else "hybrid"
    }
