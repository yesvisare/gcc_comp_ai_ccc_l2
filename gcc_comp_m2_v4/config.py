"""
Configuration management for L3 M2.4: Security Testing & Threat Modeling

Loads environment variables and initializes external service clients.
SERVICE detection: OPENAI (primary LLM) + PINECONE (vector database)
"""

import os
import logging
from typing import Optional, Any, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# SERVICE DETECTION - Multi-service module
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"

# Offline mode for local testing
OFFLINE = os.getenv("OFFLINE", "false").lower() == "true"

def init_clients() -> Dict[str, Any]:
    """
    Initialize external service clients based on environment config.

    Returns:
        Dict containing initialized clients or None if disabled

    Services:
        - openai: OpenAI client for LLM testing
        - pinecone: Pinecone client for vector database
    """
    clients = {}

    if OFFLINE:
        logger.warning("⚠️ OFFLINE mode enabled - skipping all client initialization")
        return clients

    # Initialize OpenAI client
    if OPENAI_ENABLED:
        openai_key = os.getenv("OPENAI_API_KEY")

        if not openai_key:
            logger.warning("⚠️ OPENAI_API_KEY not found - OpenAI client unavailable")
        else:
            try:
                from openai import OpenAI
                clients["openai"] = OpenAI(api_key=openai_key)
                logger.info("✓ OpenAI client initialized")
            except ImportError:
                logger.error("❌ openai package not installed - run: pip install openai")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
    else:
        logger.info("ℹ️ OPENAI_ENABLED=false - skipping OpenAI initialization")

    # Initialize Pinecone client
    if PINECONE_ENABLED:
        pinecone_key = os.getenv("PINECONE_API_KEY")
        pinecone_env = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")

        if not pinecone_key:
            logger.warning("⚠️ PINECONE_API_KEY not found - Pinecone client unavailable")
        else:
            try:
                from pinecone import Pinecone
                clients["pinecone"] = Pinecone(api_key=pinecone_key, environment=pinecone_env)
                logger.info("✓ Pinecone client initialized")
            except ImportError:
                logger.error("❌ pinecone-client package not installed - run: pip install pinecone-client")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Pinecone client: {e}")
    else:
        logger.info("ℹ️ PINECONE_ENABLED=false - skipping Pinecone initialization")

    if not clients:
        logger.warning("⚠️ No service clients initialized - module will run in offline mode")

    return clients

# Global clients dict
CLIENTS = init_clients()

# Security testing configuration
SONAR_TOKEN = os.getenv("SONAR_TOKEN")
DEFECTDOJO_URL = os.getenv("DEFECTDOJO_URL", "http://localhost:8080")
DEFECTDOJO_API_KEY = os.getenv("DEFECTDOJO_API_KEY")

# Pinecone index configuration
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "gcc-security-test")

# Logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
