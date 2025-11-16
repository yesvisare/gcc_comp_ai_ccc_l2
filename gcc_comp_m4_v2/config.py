"""
Configuration management for L3 M4.2: Vendor Risk Assessment

Loads environment variables for local processing.
This module operates entirely offline - no external LLM/vector database services required.

Optional integrations:
- PostgreSQL for vendor registry storage
- sentence-transformers for DPA clause detection (local models)
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration (optional - for production deployments)
DATABASE_URL = os.getenv("DATABASE_URL", None)
if DATABASE_URL:
    logger.info("Database URL configured for vendor registry storage")
else:
    logger.info("No database URL configured - assessments stored in memory only")

# Optional: sentence-transformers for DPA clause detection (local model)
USE_DPA_ANALYSIS = os.getenv("USE_DPA_ANALYSIS", "false").lower() == "true"
if USE_DPA_ANALYSIS:
    logger.info("DPA clause analysis enabled (uses local sentence-transformers model)")
else:
    logger.info("DPA clause analysis disabled")

# Reporting configuration
REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "./reports")
os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
logger.info(f"Report output directory: {REPORT_OUTPUT_DIR}")


def get_config() -> Dict[str, Any]:
    """
    Get application configuration.

    Returns:
        Dict containing all configuration parameters
    """
    return {
        'log_level': LOG_LEVEL,
        'database_url': DATABASE_URL,
        'use_dpa_analysis': USE_DPA_ANALYSIS,
        'report_output_dir': REPORT_OUTPUT_DIR
    }


def init_database() -> Optional[Any]:
    """
    Initialize database connection (optional).

    Returns:
        Database connection object or None if not configured
    """
    if not DATABASE_URL:
        logger.info("Skipping database initialization - no DATABASE_URL configured")
        return None

    try:
        # PostgreSQL connection would go here
        # Example: import psycopg2
        # conn = psycopg2.connect(DATABASE_URL)
        logger.info("Database connection initialized (placeholder)")
        return None  # Replace with actual connection
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return None


# Initialize optional components
DB_CONNECTION = init_database()

logger.info("Configuration loaded successfully")
