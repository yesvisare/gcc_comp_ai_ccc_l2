"""
Configuration for L3 M3.2: Automated Compliance Testing

Manages environment variables and service availability checks for:
- Open Policy Agent (OPA) - requires binary installation
- Presidio - optional Python library for enhanced PII detection
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def get_config() -> Dict[str, any]:
    """
    Get configuration from environment variables.

    Returns:
        Configuration dictionary with OPA and Presidio settings
    """
    config = {
        # OPA Configuration (requires OPA binary installed)
        "opa_enabled": os.getenv("OPA_ENABLED", "false").lower() == "true",
        "opa_binary_path": os.getenv("OPA_BINARY_PATH", "opa"),
        "opa_policy_path": os.getenv("OPA_POLICY_PATH", "./policies"),

        # Presidio Configuration (optional Python enhancement)
        "presidio_enabled": os.getenv("PRESIDIO_ENABLED", "false").lower() == "true",

        # Logging Configuration
        "log_level": os.getenv("LOG_LEVEL", "INFO"),

        # API Settings
        "api_timeout": int(os.getenv("API_TIMEOUT", "30")),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),

        # Test Configuration
        "run_tests_on_startup": os.getenv("RUN_TESTS_ON_STARTUP", "false").lower() == "true",
        "test_coverage_threshold": float(os.getenv("TEST_COVERAGE_THRESHOLD", "95.0"))
    }

    logger.info(
        f"Loaded config: OPA_ENABLED={config['opa_enabled']}, "
        f"PRESIDIO_ENABLED={config['presidio_enabled']}"
    )

    return config


def check_opa_availability() -> bool:
    """
    Check if OPA binary is available and executable.

    Returns:
        True if OPA is available, False otherwise
    """
    config = get_config()

    if not config["opa_enabled"]:
        logger.warning("⚠️ OPA not enabled in configuration")
        return False

    # Check if OPA binary exists
    import shutil
    opa_path = shutil.which(config["opa_binary_path"])

    if not opa_path:
        logger.warning(
            f"⚠️ OPA binary not found at '{config['opa_binary_path']}' - "
            f"Install from: https://www.openpolicyagent.org/docs/latest/"
        )
        return False

    logger.info(f"✓ OPA binary found at: {opa_path}")
    return True


def check_presidio_availability() -> bool:
    """
    Check if Presidio libraries are available.

    Returns:
        True if Presidio is available, False otherwise
    """
    config = get_config()

    if not config["presidio_enabled"]:
        logger.info("ℹ️ Presidio not enabled (using regex-based PII detection)")
        return False

    try:
        import presidio_analyzer
        import presidio_anonymizer
        logger.info("✓ Presidio libraries available")
        return True
    except ImportError:
        logger.warning(
            "⚠️ Presidio libraries not installed - "
            "Install with: pip install presidio-analyzer presidio-anonymizer"
        )
        return False


def check_service_availability() -> Dict[str, bool]:
    """
    Check availability of all services.

    Returns:
        Dictionary with service availability status
    """
    availability = {
        "opa": check_opa_availability(),
        "presidio": check_presidio_availability()
    }

    logger.info(f"Service availability: {availability}")
    return availability


def get_opa_client():
    """
    Get OPA client/engine if available.

    In a production environment, this would return a configured
    OPA client. For now, it returns a simple engine wrapper.

    Returns:
        OPA engine instance or None
    """
    if not check_opa_availability():
        logger.warning("⚠️ OPA not available - using simulated policy engine")
        return None

    try:
        from src.l3_m3_monitoring_reporting import OPAPolicyEngine
        config = get_config()
        engine = OPAPolicyEngine(policy_path=config["opa_policy_path"])
        logger.info("✓ OPA engine initialized")
        return engine
    except Exception as e:
        logger.error(f"Failed to initialize OPA engine: {e}")
        return None


def get_presidio_client():
    """
    Get Presidio analyzer if available.

    Returns:
        Presidio AnalyzerEngine or None
    """
    if not check_presidio_availability():
        return None

    try:
        from presidio_analyzer import AnalyzerEngine
        analyzer = AnalyzerEngine()
        logger.info("✓ Presidio analyzer initialized")
        return analyzer
    except Exception as e:
        logger.error(f"Failed to initialize Presidio: {e}")
        return None


def setup_logging():
    """
    Configure logging based on environment settings.
    """
    config = get_config()
    log_level = getattr(logging, config["log_level"].upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info(f"Logging configured at {config['log_level']} level")


# Initialize logging on module import
setup_logging()
