"""
Configuration management for L3 M4.4: Compliance Maturity & Continuous Improvement

Loads environment variables and initializes optional Prometheus/Grafana integration
for metrics visualization. All core functionality works locally without external services.
"""

import os
import logging
from typing import Optional, Any, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Optional Prometheus/Grafana integration for metrics visualization
# Note: This module works fully offline - Prometheus is only for production dashboards
PROMETHEUS_ENABLED = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"
PROMETHEUS_GATEWAY = os.getenv("PROMETHEUS_GATEWAY", "http://localhost:9091")

# Grafana for dashboard visualization (optional)
GRAFANA_ENABLED = os.getenv("GRAFANA_ENABLED", "false").lower() == "true"
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY", "")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Assessment configuration
MAX_CONCURRENT_INITIATIVES = int(os.getenv("MAX_CONCURRENT_INITIATIVES", "3"))
PDCA_CYCLE_WEEKS = int(os.getenv("PDCA_CYCLE_WEEKS", "12"))

# Metric targets (configurable)
METRIC_TARGETS = {
    "pii_detection_accuracy": float(os.getenv("TARGET_PII_ACCURACY", "99.0")),
    "audit_trail_completeness": float(os.getenv("TARGET_AUDIT_COMPLETENESS", "99.5")),
    "access_violations": float(os.getenv("TARGET_ACCESS_VIOLATIONS", "0.1")),
    "incident_mttr": float(os.getenv("TARGET_MTTR_HOURS", "4.0")),
    "compliance_test_coverage": float(os.getenv("TARGET_TEST_COVERAGE", "95.0")),
    "training_completion_rate": float(os.getenv("TARGET_TRAINING_COMPLETION", "100.0"))
}


def init_prometheus_client() -> Optional[Any]:
    """
    Initialize Prometheus Pushgateway client if enabled.

    Returns:
        Prometheus client or None if disabled
    """
    if not PROMETHEUS_ENABLED:
        logger.info("âš ï¸ Prometheus disabled - metrics will be local only")
        return None

    try:
        from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

        registry = CollectorRegistry()
        logger.info(f"âœ" Prometheus client initialized (gateway: {PROMETHEUS_GATEWAY})")

        return {
            "registry": registry,
            "push_to_gateway": push_to_gateway,
            "Gauge": Gauge
        }
    except ImportError:
        logger.warning("âš ï¸ prometheus_client not installed - install with: pip install prometheus-client")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Prometheus client: {e}")
        return None


def init_grafana_client() -> Optional[Any]:
    """
    Initialize Grafana API client if enabled.

    Returns:
        Grafana client or None if disabled
    """
    if not GRAFANA_ENABLED or not GRAFANA_API_KEY:
        logger.info("âš ï¸ Grafana disabled - dashboards will not be auto-created")
        return None

    try:
        import requests

        # Verify connection
        response = requests.get(
            f"{GRAFANA_URL}/api/health",
            headers={"Authorization": f"Bearer {GRAFANA_API_KEY}"},
            timeout=5
        )

        if response.status_code == 200:
            logger.info(f"âœ" Grafana client initialized (URL: {GRAFANA_URL})")
            return {
                "url": GRAFANA_URL,
                "api_key": GRAFANA_API_KEY,
                "session": requests.Session()
            }
        else:
            logger.warning(f"âš ï¸ Grafana health check failed: {response.status_code}")
            return None

    except ImportError:
        logger.warning("âš ï¸ requests library not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Grafana client: {e}")
        return None


# Initialize clients (optional - module works without them)
PROMETHEUS_CLIENT = init_prometheus_client()
GRAFANA_CLIENT = init_grafana_client()


def get_config_summary() -> Dict[str, Any]:
    """
    Get configuration summary for diagnostics.

    Returns:
        Dict containing current configuration state
    """
    return {
        "prometheus_enabled": PROMETHEUS_ENABLED,
        "prometheus_available": PROMETHEUS_CLIENT is not None,
        "grafana_enabled": GRAFANA_ENABLED,
        "grafana_available": GRAFANA_CLIENT is not None,
        "max_concurrent_initiatives": MAX_CONCURRENT_INITIATIVES,
        "pdca_cycle_weeks": PDCA_CYCLE_WEEKS,
        "metric_targets": METRIC_TARGETS,
        "log_level": LOG_LEVEL
    }


def push_metric_to_prometheus(metric_name: str, value: float, labels: Optional[Dict[str, str]] = None) -> bool:
    """
    Push metric to Prometheus Pushgateway if enabled.

    Args:
        metric_name: Name of the metric
        value: Metric value
        labels: Optional labels dict

    Returns:
        True if pushed successfully, False otherwise
    """
    if not PROMETHEUS_CLIENT:
        logger.debug(f"Prometheus disabled - skipping metric {metric_name}")
        return False

    try:
        registry = PROMETHEUS_CLIENT["registry"]
        Gauge = PROMETHEUS_CLIENT["Gauge"]
        push_to_gateway = PROMETHEUS_CLIENT["push_to_gateway"]

        # Create gauge with labels
        gauge = Gauge(
            metric_name.replace(" ", "_").lower(),
            f"Compliance metric: {metric_name}",
            labelnames=list(labels.keys()) if labels else [],
            registry=registry
        )

        if labels:
            gauge.labels(**labels).set(value)
        else:
            gauge.set(value)

        # Push to gateway
        push_to_gateway(
            PROMETHEUS_GATEWAY,
            job='compliance_maturity',
            registry=registry
        )

        logger.debug(f"Pushed metric to Prometheus: {metric_name}={value}")
        return True

    except Exception as e:
        logger.error(f"Failed to push metric to Prometheus: {e}")
        return False
