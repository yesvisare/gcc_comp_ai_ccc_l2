"""
Configuration management for L3 M2: Security_Access_Control

Loads environment variables and validates OAuth/JWT/Session configuration.
Provides centralized config objects for app.py and core modules.
"""

import os
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Environment Detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# OAuth 2.0 Configuration
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
OAUTH_AUTHORIZATION_ENDPOINT = os.getenv(
    "OAUTH_AUTHORIZATION_ENDPOINT",
    "https://your-idp.okta.com/oauth2/v1/authorize"
)
OAUTH_TOKEN_ENDPOINT = os.getenv(
    "OAUTH_TOKEN_ENDPOINT",
    "https://your-idp.okta.com/oauth2/v1/token"
)
OAUTH_USERINFO_ENDPOINT = os.getenv(
    "OAUTH_USERINFO_ENDPOINT",
    "https://your-idp.okta.com/oauth2/v1/userinfo"
)
OAUTH_ISSUER = os.getenv("OAUTH_ISSUER", "https://your-idp.okta.com")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "RS256")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "api://default")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

# Session Management
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "")
SESSION_TIMEOUT_SECONDS = int(os.getenv("SESSION_TIMEOUT_SECONDS", "3600"))
MAX_CONCURRENT_SESSIONS = int(os.getenv("MAX_CONCURRENT_SESSIONS", "3"))

# Database Configuration (for user/tenant metadata)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/gcc_auth")
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Security Settings
ENABLE_IP_VALIDATION = os.getenv("ENABLE_IP_VALIDATION", "true").lower() == "true"
ENABLE_USER_AGENT_VALIDATION = os.getenv("ENABLE_USER_AGENT_VALIDATION", "false").lower() == "true"
REQUIRE_MFA = os.getenv("REQUIRE_MFA", "false").lower() == "true"


def validate_oauth_config() -> bool:
    """
    Validate OAuth configuration for production readiness.

    Returns:
        True if OAuth is properly configured, False otherwise
    """
    required_vars = [
        ("OAUTH_CLIENT_ID", OAUTH_CLIENT_ID),
        ("OAUTH_CLIENT_SECRET", OAUTH_CLIENT_SECRET),
        ("OAUTH_REDIRECT_URI", OAUTH_REDIRECT_URI),
    ]

    missing = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing.append(var_name)

    if missing:
        logger.warning(
            f"⚠️ OAuth configuration incomplete - missing: {', '.join(missing)}\n"
            f"   Running in demo mode with simulated responses."
        )
        return False

    logger.info("✓ OAuth configuration validated")
    return True


def validate_jwt_config() -> bool:
    """
    Validate JWT configuration.

    Returns:
        True if JWT is properly configured
    """
    if not JWT_SECRET_KEY:
        logger.warning(
            "⚠️ JWT_SECRET_KEY not set - token validation will fail\n"
            "   Set JWT_SECRET_KEY in .env for production use"
        )
        return False

    logger.info(f"✓ JWT configuration validated (algorithm: {JWT_ALGORITHM})")
    return True


def validate_session_config() -> bool:
    """
    Validate session management configuration.

    Returns:
        True if session config is valid
    """
    if not SESSION_SECRET_KEY:
        logger.warning(
            "⚠️ SESSION_SECRET_KEY not set - using insecure default\n"
            "   Set SESSION_SECRET_KEY in .env for production use"
        )
        return False

    logger.info(f"✓ Session configuration validated (Redis: {REDIS_HOST}:{REDIS_PORT})")
    return True


def get_oauth_config() -> Dict[str, Any]:
    """
    Get OAuth client configuration dictionary.

    Returns:
        Dictionary with OAuth settings for OAuthClient initialization
    """
    return {
        "client_id": OAUTH_CLIENT_ID,
        "client_secret": OAUTH_CLIENT_SECRET,
        "redirect_uri": OAUTH_REDIRECT_URI,
        "authorization_endpoint": OAUTH_AUTHORIZATION_ENDPOINT,
        "token_endpoint": OAUTH_TOKEN_ENDPOINT,
        "userinfo_endpoint": OAUTH_USERINFO_ENDPOINT,
        "issuer": OAUTH_ISSUER,
    }


def get_jwt_config() -> Dict[str, Any]:
    """
    Get JWT validator configuration dictionary.

    Returns:
        Dictionary with JWT settings for JWTValidator initialization
    """
    return {
        "jwt_secret": JWT_SECRET_KEY,
        "jwt_algorithm": JWT_ALGORITHM,
        "issuer": OAUTH_ISSUER,
        "audience": JWT_AUDIENCE,
    }


def get_session_config() -> Dict[str, Any]:
    """
    Get session manager configuration dictionary.

    Returns:
        Dictionary with session settings for SessionManager initialization
    """
    return {
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT,
        "redis_password": REDIS_PASSWORD,
        "redis_db": REDIS_DB,
        "session_timeout": SESSION_TIMEOUT_SECONDS,
        "max_concurrent_sessions": MAX_CONCURRENT_SESSIONS,
        "enable_ip_validation": ENABLE_IP_VALIDATION,
        "enable_user_agent_validation": ENABLE_USER_AGENT_VALIDATION,
    }


def validate_all_config() -> Dict[str, bool]:
    """
    Validate all configuration sections.

    Returns:
        Dictionary with validation status for each section
    """
    validation_results = {
        "oauth": validate_oauth_config(),
        "jwt": validate_jwt_config(),
        "session": validate_session_config(),
    }

    all_valid = all(validation_results.values())

    if all_valid:
        logger.info("✓ All configuration validated successfully")
    else:
        failed = [k for k, v in validation_results.items() if not v]
        logger.warning(f"⚠️ Configuration validation failed for: {', '.join(failed)}")

    return validation_results


def get_full_config() -> Dict[str, Any]:
    """
    Get complete configuration for application initialization.

    Returns:
        Dictionary with all configuration sections
    """
    return {
        "environment": ENVIRONMENT,
        "debug": DEBUG_MODE,
        "oauth": get_oauth_config(),
        "jwt": get_jwt_config(),
        "session": get_session_config(),
        "api": {
            "host": API_HOST,
            "port": API_PORT,
        },
        "database": {
            "url": DATABASE_URL,
            "pool_size": DATABASE_POOL_SIZE,
        },
        "security": {
            "require_mfa": REQUIRE_MFA,
        },
    }


# Validate configuration on module import
if __name__ != "__main__":
    validation_status = validate_all_config()

    # In development, provide helpful warnings
    if ENVIRONMENT == "development" and not all(validation_status.values()):
        logger.info(
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  L3 M2: Security_Access_Control - Configuration Status\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "\n"
            "⚠️  Running in DEVELOPMENT mode with incomplete configuration\n"
            "\n"
            "To enable full OAuth functionality:\n"
            "  1. Copy .env.example to .env\n"
            "  2. Configure OAuth client credentials from your IdP\n"
            "  3. Set JWT_SECRET_KEY and SESSION_SECRET_KEY\n"
            "  4. Start Redis: docker run -p 6379:6379 redis:7-alpine\n"
            "\n"
            "Current status:\n"
            f"  • OAuth:   {'✓' if validation_status['oauth'] else '✗'}\n"
            f"  • JWT:     {'✓' if validation_status['jwt'] else '✗'}\n"
            f"  • Session: {'✓' if validation_status['session'] else '✗'}\n"
            "\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )


if __name__ == "__main__":
    # CLI for configuration validation
    import sys

    print("L3 M2: Security_Access_Control - Configuration Validator\n")

    results = validate_all_config()

    print("\nConfiguration Status:")
    print(f"  OAuth:   {'✓ Valid' if results['oauth'] else '✗ Invalid'}")
    print(f"  JWT:     {'✓ Valid' if results['jwt'] else '✗ Invalid'}")
    print(f"  Session: {'✓ Valid' if results['session'] else '✗ Invalid'}")

    print(f"\nEnvironment: {ENVIRONMENT}")
    print(f"Debug Mode:  {DEBUG_MODE}")

    if not all(results.values()):
        print("\n⚠️  Some configuration is missing - see warnings above")
        sys.exit(1)
    else:
        print("\n✓ All configuration valid - ready for production")
        sys.exit(0)
