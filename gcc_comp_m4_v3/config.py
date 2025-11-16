"""
Configuration management for L3 M4.3: Change Management & Compliance

Loads environment variables and initializes database connection.
No external API services required - this is an internal governance tool.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ============================================================================
# Environment Configuration
# ============================================================================

# Database configuration (SQLite for demo, PostgreSQL for production)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./changes.db")

# Extract database path for SQLite
if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = DATABASE_URL.replace("sqlite:///", "")
else:
    # For PostgreSQL or other databases, use full URL
    DB_PATH = DATABASE_URL

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Offline mode for notebooks/testing
OFFLINE = os.getenv("OFFLINE", "false").lower() == "true"

# ============================================================================
# Logging Setup
# ============================================================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger.info(f"Configuration loaded:")
logger.info(f"  DATABASE_URL: {DATABASE_URL}")
logger.info(f"  LOG_LEVEL: {LOG_LEVEL}")
logger.info(f"  OFFLINE: {OFFLINE}")

# ============================================================================
# Database Initialization
# ============================================================================

def get_db_path() -> str:
    """
    Get database path for SQLite or connection string for PostgreSQL.

    Returns:
        Database path or connection string
    """
    return DB_PATH


def is_offline_mode() -> bool:
    """
    Check if running in offline mode (for notebooks/testing).

    Returns:
        True if offline mode enabled
    """
    return OFFLINE
