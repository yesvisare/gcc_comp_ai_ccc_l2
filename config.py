"""
Configuration management for L3_M1 Compliance Foundations RAG Systems.
Handles environment variables and service client initialization.

Services:
- PRESIDIO (local PII detection - requires spaCy models)
- OPENAI (embeddings generation)
- PINECONE (vector database)
- PostgreSQL (audit trails)
- Redis (caching)
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================

# Presidio (local PII detection)
PRESIDIO_ENABLED = os.getenv("PRESIDIO_ENABLED", "false").lower() == "true"

# OpenAI (embeddings)
OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Pinecone (vector database)
PINECONE_ENABLED = os.getenv("PINECONE_ENABLED", "false").lower() == "true"
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", "")

# PostgreSQL (audit trails)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Redis (caching)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Airflow (retention policies)
AIRFLOW_ENABLED = os.getenv("AIRFLOW_ENABLED", "false").lower() == "true"
AIRFLOW_HOME = os.getenv("AIRFLOW_HOME", "")

# Data Residency
EU_REGION = os.getenv("EU_REGION", "eu-central-1")
INDIA_REGION = os.getenv("INDIA_REGION", "ap-south-1")
US_REGION = os.getenv("US_REGION", "us-east-1")


# ============================================================================
# CLIENT INITIALIZATION
# ============================================================================

def get_presidio_analyzer():
    """
    Initialize and return Presidio analyzer (local).
    Returns None if Presidio is disabled or spaCy models missing.
    """
    if not PRESIDIO_ENABLED:
        logger.warning("⚠️ Presidio disabled via PRESIDIO_ENABLED=false")
        return None

    try:
        from presidio_analyzer import AnalyzerEngine
        analyzer = AnalyzerEngine()
        logger.info("✅ Presidio analyzer initialized (local)")
        return analyzer
    except ImportError:
        logger.warning("⚠️ Presidio not installed. Install: pip install presidio-analyzer presidio-anonymizer")
        return None
    except Exception as e:
        logger.warning(f"⚠️ Presidio initialization failed: {e}")
        logger.warning("   Ensure spaCy model installed: python -m spacy download en_core_web_lg")
        return None


def get_openai_client():
    """
    Initialize and return OpenAI client.
    Returns None if OpenAI is disabled or API key missing.
    """
    if not OPENAI_ENABLED:
        logger.warning("⚠️ OpenAI disabled via OPENAI_ENABLED=false")
        return None

    if not OPENAI_API_KEY:
        logger.warning("⚠️ OPENAI_API_KEY not set")
        return None

    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        logger.info("✅ OpenAI client initialized")
        return openai
    except ImportError:
        logger.warning("⚠️ OpenAI library not installed. Install: pip install openai")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI: {e}")
        return None


def get_pinecone_client():
    """
    Initialize and return Pinecone client.
    Returns None if Pinecone is disabled or credentials missing.
    """
    if not PINECONE_ENABLED:
        logger.warning("⚠️ Pinecone disabled via PINECONE_ENABLED=false")
        return None

    if not PINECONE_API_KEY or not PINECONE_ENV:
        logger.warning("⚠️ PINECONE_API_KEY or PINECONE_ENVIRONMENT not set")
        return None

    try:
        import pinecone
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        logger.info("✅ Pinecone client initialized")
        return pinecone
    except ImportError:
        logger.warning("⚠️ Pinecone library not installed. Install: pip install pinecone-client")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize Pinecone: {e}")
        return None


def get_database_connection():
    """
    Initialize and return PostgreSQL connection.
    Returns None if DATABASE_URL not set.
    """
    if not DATABASE_URL:
        logger.warning("⚠️ DATABASE_URL not set")
        return None

    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("✅ PostgreSQL connection established")
        return conn
    except ImportError:
        logger.warning("⚠️ psycopg2 not installed. Install: pip install psycopg2-binary")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        return None


def get_redis_client():
    """
    Initialize and return Redis client.
    Returns None if connection fails.
    """
    try:
        import redis
        client = redis.from_url(REDIS_URL)
        client.ping()  # Test connection
        logger.info("✅ Redis client initialized")
        return client
    except ImportError:
        logger.warning("⚠️ Redis library not installed. Install: pip install redis")
        return None
    except Exception as e:
        logger.warning(f"⚠️ Failed to connect to Redis: {e}")
        return None


# ============================================================================
# INITIALIZE CLIENTS AT MODULE LOAD
# ============================================================================

presidio_analyzer = get_presidio_analyzer()
openai_client = get_openai_client()
pinecone_client = get_pinecone_client()
database_connection = get_database_connection()
redis_client = get_redis_client()


# ============================================================================
# HEALTH CHECK
# ============================================================================

def get_service_health() -> dict:
    """
    Get health status of all services.

    Returns:
        Dictionary with service availability status
    """
    return {
        "presidio": presidio_analyzer is not None,
        "openai": openai_client is not None,
        "pinecone": pinecone_client is not None,
        "database": database_connection is not None,
        "redis": redis_client is not None,
        "airflow": AIRFLOW_ENABLED
    }
