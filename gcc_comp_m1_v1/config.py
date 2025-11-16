"""
Configuration management for L3 M1.1: Why Compliance Matters in GCC RAG Systems

Loads environment variables and initializes service clients for:
- Presidio (PII detection)
- OpenAI (embeddings and risk analysis)
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Presidio Configuration
PRESIDIO_ENABLED = os.getenv("PRESIDIO_ENABLED", "false").lower() == "true"

# OpenAI Configuration
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize Presidio client if enabled
presidio_analyzer = None
if PRESIDIO_ENABLED:
    try:
        from presidio_analyzer import AnalyzerEngine
        presidio_analyzer = AnalyzerEngine()
        logger.info("✅ Presidio analyzer initialized successfully")
    except ImportError:
        logger.warning("⚠️ Presidio library not installed. Install with: pip install presidio-analyzer")
        PRESIDIO_ENABLED = False
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize Presidio: {e}")
        PRESIDIO_ENABLED = False
else:
    logger.info("⚠️ Presidio disabled - set PRESIDIO_ENABLED=true to enable enhanced PII detection")

# Initialize OpenAI client if enabled
openai_client = None
if OPENAI_ENABLED:
    if not OPENAI_API_KEY:
        logger.warning("⚠️ OPENAI_ENABLED=true but OPENAI_API_KEY not set")
        OPENAI_ENABLED = False
    else:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            openai_client = openai
            logger.info("✅ OpenAI client initialized successfully")
        except ImportError:
            logger.warning("⚠️ OpenAI library not installed. Install with: pip install openai")
            OPENAI_ENABLED = False
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize OpenAI: {e}")
            OPENAI_ENABLED = False
else:
    logger.info("⚠️ OpenAI disabled - set OPENAI_ENABLED=true and OPENAI_API_KEY to enable")


def get_presidio_analyzer():
    """
    Get Presidio analyzer instance.

    Returns:
        AnalyzerEngine instance or None if not configured

    Raises:
        RuntimeError: If Presidio is not enabled or failed to initialize
    """
    if not PRESIDIO_ENABLED or not presidio_analyzer:
        raise RuntimeError(
            "Presidio not configured. Set PRESIDIO_ENABLED=true and install presidio-analyzer"
        )
    return presidio_analyzer


def get_openai_client():
    """
    Get OpenAI client instance.

    Returns:
        OpenAI client or None if not configured

    Raises:
        RuntimeError: If OpenAI is not enabled or failed to initialize
    """
    if not OPENAI_ENABLED or not openai_client:
        raise RuntimeError(
            "OpenAI not configured. Set OPENAI_ENABLED=true and OPENAI_API_KEY"
        )
    return openai_client


def get_config_summary() -> dict:
    """
    Get summary of current configuration.

    Returns:
        Dictionary with configuration status
    """
    return {
        "presidio_enabled": PRESIDIO_ENABLED,
        "openai_enabled": OPENAI_ENABLED,
        "log_level": LOG_LEVEL,
        "services_available": {
            "presidio": PRESIDIO_ENABLED,
            "openai": OPENAI_ENABLED
        }
    }
