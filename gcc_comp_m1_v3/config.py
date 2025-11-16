"""
Configuration management for L3 M1.3: Regulatory Frameworks Deep Dive

Handles environment variables and configuration settings.
No external services required - all processing is local.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_config() -> Dict[str, Any]:
    """
    Return configuration dictionary for the application.

    No external API keys needed - all compliance analysis is performed locally
    using Pydantic models and custom analyzer classes.
    """
    config = {
        "module": "L3_M1_Compliance_Foundations",
        "version": "1.0.0",
        "frameworks": ["GDPR", "SOC2", "ISO27001", "HIPAA"],
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "mode": "OFFLINE",  # All processing is local
        "description": "Multi-framework compliance analyzer for RAG systems"
    }

    logger.info("Configuration loaded successfully (OFFLINE mode)")
    return config


def validate_config() -> bool:
    """
    Validate configuration settings.

    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        config = get_config()

        # Validate required fields
        required_fields = ["module", "version", "frameworks"]
        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required config field: {field}")
                return False

        # Validate frameworks
        expected_frameworks = ["GDPR", "SOC2", "ISO27001", "HIPAA"]
        if config["frameworks"] != expected_frameworks:
            logger.warning(f"Framework list differs from expected: {config['frameworks']}")

        logger.info("Configuration validation successful")
        return True

    except Exception as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Test configuration
    logging.basicConfig(level=logging.INFO)
    config = get_config()
    print(f"Configuration: {config}")
    print(f"Valid: {validate_config()}")
