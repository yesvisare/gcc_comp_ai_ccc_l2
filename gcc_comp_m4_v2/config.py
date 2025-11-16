"""
Configuration management for L3 M4.2: Vendor Risk Assessment

This module manages application configuration using environment variables.
No external API services required - this module uses OFFLINE processing only.
"""
import os
from typing import Dict, Any

def get_config() -> Dict[str, Any]:
    """
    Get application configuration from environment variables.

    Returns:
        Dictionary with all configuration settings
    """
    return {
        # Application settings
        "environment": os.getenv("ENVIRONMENT", "development"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "timeout": int(os.getenv("TIMEOUT", "30")),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),

        # Database settings (if using PostgreSQL for vendor registry)
        "database": {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "name": os.getenv("DB_NAME", "vendor_risk_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
        },

        # Monitoring settings
        "quarterly_review_days": int(os.getenv("QUARTERLY_REVIEW_DAYS", "90")),
        "certification_warning_days": int(os.getenv("CERTIFICATION_WARNING_DAYS", "90")),

        # Risk thresholds
        "risk_thresholds": {
            "low": float(os.getenv("RISK_THRESHOLD_LOW", "90")),
            "medium": float(os.getenv("RISK_THRESHOLD_MEDIUM", "70")),
            "high": float(os.getenv("RISK_THRESHOLD_HIGH", "50")),
        },

        # Notification settings
        "notifications_enabled": os.getenv("NOTIFICATIONS_ENABLED", "false").lower() == "true",
        "smtp_host": os.getenv("SMTP_HOST", ""),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "alert_email": os.getenv("ALERT_EMAIL", ""),
    }


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration settings.

    Args:
        config: Configuration dictionary

    Returns:
        True if configuration is valid

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate environment
    valid_environments = ["development", "staging", "production"]
    if config["environment"] not in valid_environments:
        raise ValueError(f"Invalid environment: {config['environment']}")

    # Validate log level
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config["log_level"] not in valid_log_levels:
        raise ValueError(f"Invalid log level: {config['log_level']}")

    # Validate timeout
    if config["timeout"] <= 0:
        raise ValueError("Timeout must be positive")

    # Validate risk thresholds
    thresholds = config["risk_thresholds"]
    if not (0 < thresholds["high"] < thresholds["medium"] < thresholds["low"] <= 100):
        raise ValueError("Invalid risk thresholds - must be: 0 < high < medium < low <= 100")

    return True
