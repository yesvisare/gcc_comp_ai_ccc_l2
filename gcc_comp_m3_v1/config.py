"""
Configuration management for L3 M3.1 Compliance Monitoring

Loads environment variables and initializes Prometheus/Grafana clients for
compliance metrics collection and dashboard visualization.

Service Detection: PROMETHEUS (metrics) + GRAFANA (visualization)
"""

import os
import logging
from typing import Optional, Any, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Prometheus configuration
PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"
PROMETHEUS_PUSHGATEWAY_URL = os.getenv("PROMETHEUS_PUSHGATEWAY_URL", "http://localhost:9091")
PROMETHEUS_RETENTION_DAYS = int(os.getenv("PROMETHEUS_RETENTION_DAYS", "395"))  # 13 months for SOX

# Grafana configuration
GRAFANA_ENABLED = os.getenv("GRAFANA_ENABLED", "false").lower() == "true"
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY", "")

# OPA (Open Policy Agent) configuration
OPA_ENABLED = os.getenv("OPA_ENABLED", "false").lower() == "true"
OPA_URL = os.getenv("OPA_URL", "http://localhost:8181")

# Alert manager configuration
ALERTMANAGER_ENABLED = os.getenv("ALERTMANAGER_ENABLED", "false").lower() == "true"
ALERTMANAGER_URL = os.getenv("ALERTMANAGER_URL", "http://localhost:9093")
PAGERDUTY_API_KEY = os.getenv("PAGERDUTY_API_KEY", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Compliance thresholds
COMPLIANCE_THRESHOLDS = {
    "audit_trail_completeness": float(os.getenv("THRESHOLD_AUDIT_COMPLETENESS", "99.0")),
    "pii_detection_precision": float(os.getenv("THRESHOLD_PII_PRECISION", "95.0")),
    "pii_detection_recall": float(os.getenv("THRESHOLD_PII_RECALL", "99.0")),
    "access_control_violations": float(os.getenv("THRESHOLD_ACCESS_VIOLATIONS", "0.1")),
    "encryption_coverage": float(os.getenv("THRESHOLD_ENCRYPTION", "100.0")),
    "certificate_expiry_days": int(os.getenv("THRESHOLD_CERT_EXPIRY", "30"))
}

# Offline mode (for local development/testing)
OFFLINE = os.getenv("OFFLINE", "false").lower() == "true"


def init_clients() -> Dict[str, Any]:
    """
    Initialize external service clients based on environment config.

    Returns:
        Dict containing initialized clients or None if disabled/offline
    """
    clients = {}

    if OFFLINE:
        logger.warning("âš ï¸ OFFLINE mode enabled - all external services disabled")
        return clients

    # Initialize Prometheus client
    if PROMETHEUS_ENABLED:
        try:
            # In production, would initialize prometheus_client library
            # from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
            # registry = CollectorRegistry()
            # clients["prometheus_registry"] = registry

            logger.info(f"âœ" Prometheus client initialized (pushgateway: {PROMETHEUS_PUSHGATEWAY_URL})")
            clients["prometheus_url"] = PROMETHEUS_PUSHGATEWAY_URL
        except Exception as e:
            logger.error(f"Failed to initialize Prometheus client: {e}")
    else:
        logger.info("âš ï¸ Prometheus disabled - set PROMETHEUS_ENABLED=true to enable")

    # Initialize Grafana client
    if GRAFANA_ENABLED:
        try:
            if not GRAFANA_API_KEY:
                logger.warning("âš ï¸ GRAFANA_API_KEY not set - dashboard creation unavailable")
            else:
                # In production, would initialize grafana_client library
                # from grafana_client import GrafanaApi
                # clients["grafana"] = GrafanaApi.from_url(GRAFANA_URL, auth=GRAFANA_API_KEY)

                logger.info(f"âœ" Grafana client initialized (URL: {GRAFANA_URL})")
                clients["grafana_url"] = GRAFANA_URL
        except Exception as e:
            logger.error(f"Failed to initialize Grafana client: {e}")
    else:
        logger.info("âš ï¸ Grafana disabled - set GRAFANA_ENABLED=true to enable")

    # Initialize OPA client
    if OPA_ENABLED:
        try:
            # In production, would initialize OPA HTTP client
            # import requests
            # clients["opa_session"] = requests.Session()

            logger.info(f"âœ" OPA client initialized (URL: {OPA_URL})")
            clients["opa_url"] = OPA_URL
        except Exception as e:
            logger.error(f"Failed to initialize OPA client: {e}")
    else:
        logger.info("âš ï¸ OPA disabled - set OPA_ENABLED=true to enable")

    # Initialize Alert Manager client
    if ALERTMANAGER_ENABLED:
        try:
            logger.info(f"âœ" AlertManager client initialized (URL: {ALERTMANAGER_URL})")
            clients["alertmanager_url"] = ALERTMANAGER_URL

            if PAGERDUTY_API_KEY:
                clients["pagerduty_enabled"] = True
                logger.info("âœ" PagerDuty integration enabled")

            if SLACK_WEBHOOK_URL:
                clients["slack_enabled"] = True
                logger.info("âœ" Slack integration enabled")

        except Exception as e:
            logger.error(f"Failed to initialize AlertManager client: {e}")
    else:
        logger.info("âš ï¸ AlertManager disabled - set ALERTMANAGER_ENABLED=true to enable")

    return clients


# Global clients dictionary
CLIENTS = init_clients()


def get_config() -> Dict[str, Any]:
    """
    Get complete configuration dictionary.

    Returns:
        Configuration dict with all settings and clients
    """
    return {
        "prometheus": {
            "enabled": PROMETHEUS_ENABLED,
            "pushgateway_url": PROMETHEUS_PUSHGATEWAY_URL,
            "retention_days": PROMETHEUS_RETENTION_DAYS
        },
        "grafana": {
            "enabled": GRAFANA_ENABLED,
            "url": GRAFANA_URL,
            "api_key_set": bool(GRAFANA_API_KEY)
        },
        "opa": {
            "enabled": OPA_ENABLED,
            "url": OPA_URL
        },
        "alertmanager": {
            "enabled": ALERTMANAGER_ENABLED,
            "url": ALERTMANAGER_URL,
            "pagerduty_enabled": bool(PAGERDUTY_API_KEY),
            "slack_enabled": bool(SLACK_WEBHOOK_URL)
        },
        "thresholds": COMPLIANCE_THRESHOLDS,
        "offline": OFFLINE,
        "clients": CLIENTS
    }
