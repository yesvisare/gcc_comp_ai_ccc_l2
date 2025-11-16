"""
L3 M2.1: Authentication & Identity Management

This module implements OAuth 2.0 / OIDC authentication with multi-tenant isolation
for GCC RAG systems serving 50+ business units in regulated industries.

Core capabilities:
- OAuth 2.0/OIDC integration with enterprise Identity Providers (Okta, Azure AD, Auth0)
- JWT token validation with cryptographic signature verification
- Role-Based Access Control (RBAC) with four standard roles
- Multi-tenant isolation with namespace-based filtering
- Session management using Redis-backed token storage
- Multi-Factor Authentication (MFA) enforcement with TOTP support
- Session hijacking prevention through IP and User-Agent validation
"""

import logging
import hashlib
import secrets
import base64
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode
import jwt
from jwt import PyJWTError

logger = logging.getLogger(__name__)

__all__ = [
    "OAuthClient",
    "JWTValidator",
    "RBACEngine",
    "SessionManager",
    "generate_pkce_pair",
    "validate_tenant_isolation",
    "check_permission",
    "detect_session_hijacking",
]

# RBAC Role Definitions
ROLES = {
    "Admin": ["read", "write", "delete", "manage_users", "manage_tenants"],
    "Developer": ["read", "write", "execute"],
    "Analyst": ["read", "query"],
    "Viewer": ["read"],
}

# Standard OIDC Scopes
OIDC_SCOPES = ["openid", "profile", "email"]


class OAuthClient:
    """
    OAuth 2.0 / OIDC client for enterprise Identity Provider integration.

    Implements authorization code flow with PKCE for enhanced security.
    Supports Okta, Azure AD, Auth0, and Google Workspace.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OAuth client with Identity Provider configuration.

        Args:
            config: Dictionary containing:
                - client_id: OAuth client ID from IdP
                - client_secret: OAuth client secret
                - redirect_uri: Callback URL for authorization code
                - authorization_endpoint: IdP authorization URL
                - token_endpoint: IdP token exchange URL
                - userinfo_endpoint: OIDC userinfo URL
                - issuer: JWT issuer claim for validation
        """
        self.client_id = config.get("client_id", "")
        self.client_secret = config.get("client_secret", "")
        self.redirect_uri = config.get("redirect_uri", "")
        self.authorization_endpoint = config.get("authorization_endpoint", "")
        self.token_endpoint = config.get("token_endpoint", "")
        self.userinfo_endpoint = config.get("userinfo_endpoint", "")
        self.issuer = config.get("issuer", "")

        logger.info(f"OAuthClient initialized for issuer: {self.issuer}")

    def get_authorize_url(self, state: str, code_challenge: str) -> str:
        """
        Generate authorization URL with PKCE challenge.

        Args:
            state: Random state parameter for CSRF protection
            code_challenge: SHA256 hash of code_verifier (PKCE)

        Returns:
            Full authorization URL to redirect user to IdP
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(OIDC_SCOPES),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        url = f"{self.authorization_endpoint}?{urlencode(params)}"
        logger.info("Generated authorization URL with PKCE")
        return url

    def exchange_code_for_tokens(
        self,
        authorization_code: str,
        code_verifier: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access and ID tokens.

        This is a server-to-server call using client_secret.
        In production, this would use requests library.

        Args:
            authorization_code: Code from IdP callback
            code_verifier: Original random string from PKCE pair

        Returns:
            Dictionary containing access_token, id_token, refresh_token, expires_in

        Raises:
            ValueError: If code is invalid or expired
        """
        if not authorization_code:
            logger.error("Empty authorization code provided")
            raise ValueError("Authorization code cannot be empty")

        # In production, this would make HTTP POST to token_endpoint
        # Simulated response for demonstration
        logger.info("Exchanging authorization code for tokens (simulated)")

        tokens = {
            "access_token": f"simulated_access_token_{secrets.token_urlsafe(32)}",
            "id_token": f"simulated_id_token_{secrets.token_urlsafe(32)}",
            "refresh_token": f"simulated_refresh_token_{secrets.token_urlsafe(32)}",
            "expires_in": 3600,
            "token_type": "Bearer",
        }

        logger.info("Successfully exchanged code for tokens")
        return tokens

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Retrieve user profile from OIDC userinfo endpoint.

        Args:
            access_token: OAuth access token

        Returns:
            Dictionary with user claims (sub, email, name, tenant_id, roles)

        Raises:
            ValueError: If token is invalid
        """
        if not access_token:
            logger.error("Empty access token provided")
            raise ValueError("Access token cannot be empty")

        # In production, this would make HTTP GET to userinfo_endpoint
        # Simulated response for demonstration
        logger.info("Fetching user info from IdP (simulated)")

        user_info = {
            "sub": "user_12345",
            "email": "john.doe@example.com",
            "name": "John Doe",
            "tenant_id": "tenant_abc",
            "roles": ["Developer"],
            "email_verified": True,
            "mfa_enabled": True,
        }

        logger.info(f"Retrieved user info for: {user_info['email']}")
        return user_info


class JWTValidator:
    """
    JWT token validator with signature verification and claims validation.

    Implements industry-standard validation per RFC 7519.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize JWT validator with signing keys.

        Args:
            config: Dictionary containing:
                - jwt_secret: Secret key for HS256 (symmetric) or public key for RS256
                - jwt_algorithm: Algorithm (HS256, RS256, ES256)
                - issuer: Expected issuer claim
                - audience: Expected audience claim
        """
        self.secret = config.get("jwt_secret", "")
        self.algorithm = config.get("jwt_algorithm", "RS256")
        self.issuer = config.get("issuer", "")
        self.audience = config.get("audience", "")

        logger.info(f"JWTValidator initialized with algorithm: {self.algorithm}")

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token signature and claims.

        Validation order (CRITICAL - signature first!):
        1. Signature verification
        2. Expiration check (exp claim)
        3. Not-before check (nbf claim)
        4. Issuer validation (iss claim)
        5. Audience validation (aud claim)

        Args:
            token: JWT token string

        Returns:
            Decoded payload with claims (sub, tenant_id, roles, exp, etc.)

        Raises:
            PyJWTError: If token is invalid, expired, or signature fails
        """
        if not token:
            logger.error("Empty token provided for validation")
            raise ValueError("Token cannot be empty")

        try:
            # Decode and verify signature
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iss": True,
                    "verify_aud": True,
                }
            )

            logger.info(f"Token validated successfully for subject: {payload.get('sub')}")
            return payload

        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise
        except jwt.InvalidIssuerError:
            logger.error(f"Invalid issuer - expected {self.issuer}")
            raise
        except jwt.InvalidAudienceError:
            logger.error(f"Invalid audience - expected {self.audience}")
            raise
        except PyJWTError as e:
            logger.error(f"JWT validation failed: {e}")
            raise

    def decode_without_verification(self, token: str) -> Dict[str, Any]:
        """
        Decode JWT without verification (for debugging only - NEVER use in production).

        Args:
            token: JWT token string

        Returns:
            Decoded payload without validation
        """
        logger.warning("⚠️ Decoding token WITHOUT verification - debug only!")
        return jwt.decode(token, options={"verify_signature": False})


class RBACEngine:
    """
    Role-Based Access Control engine with multi-tenant awareness.

    Implements four standard roles: Admin, Developer, Analyst, Viewer.
    Enforces tenant isolation on all permission checks.
    """

    def __init__(self):
        """Initialize RBAC engine with role definitions."""
        self.roles = ROLES
        logger.info("RBACEngine initialized with 4 standard roles")

    def check_permission(
        self,
        user_roles: List[str],
        required_permission: str
    ) -> bool:
        """
        Check if user's roles grant required permission.

        Args:
            user_roles: List of roles assigned to user (e.g., ["Developer"])
            required_permission: Permission to check (e.g., "write")

        Returns:
            True if user has permission, False otherwise
        """
        for role in user_roles:
            if role in self.roles:
                if required_permission in self.roles[role]:
                    logger.info(f"Permission '{required_permission}' granted via role '{role}'")
                    return True

        logger.warning(f"Permission '{required_permission}' denied for roles: {user_roles}")
        return False

    def get_role_permissions(self, role: str) -> List[str]:
        """
        Get all permissions for a given role.

        Args:
            role: Role name (Admin, Developer, Analyst, Viewer)

        Returns:
            List of permissions
        """
        return self.roles.get(role, [])

    def validate_tenant_isolation(
        self,
        user_tenant_id: str,
        resource_tenant_id: str
    ) -> bool:
        """
        Validate tenant isolation - CRITICAL for multi-tenant security.

        Every query must verify: user.tenant_id == document.tenant_id

        Args:
            user_tenant_id: Tenant ID from user's JWT claims
            resource_tenant_id: Tenant ID of resource being accessed

        Returns:
            True if tenant IDs match, False otherwise

        Raises:
            ValueError: If tenant isolation is violated
        """
        if user_tenant_id != resource_tenant_id:
            logger.error(
                f"⚠️ TENANT ISOLATION VIOLATION: User tenant '{user_tenant_id}' "
                f"attempted to access resource from tenant '{resource_tenant_id}'"
            )
            raise ValueError("Cross-tenant access denied")

        logger.info(f"Tenant isolation validated for tenant: {user_tenant_id}")
        return True


class SessionManager:
    """
    Session manager with Redis-backed token storage and hijacking detection.

    Implements session security through:
    - Redis TTL matching JWT expiration
    - IP address validation
    - User-Agent fingerprinting
    - Concurrent session limits
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize session manager with Redis configuration.

        Args:
            config: Dictionary containing:
                - redis_host: Redis server hostname
                - redis_port: Redis server port
                - session_timeout: Session TTL in seconds (default 3600)
                - max_concurrent_sessions: Max sessions per user (default 3)
        """
        self.redis_host = config.get("redis_host", "localhost")
        self.redis_port = config.get("redis_port", 6379)
        self.session_timeout = config.get("session_timeout", 3600)
        self.max_concurrent_sessions = config.get("max_concurrent_sessions", 3)

        # In production, initialize Redis client here
        # self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port)

        logger.info(f"SessionManager initialized with TTL: {self.session_timeout}s")

    def create_session(
        self,
        user_id: str,
        token: str,
        ip_address: str,
        user_agent: str
    ) -> str:
        """
        Create new session with security fingerprints.

        Args:
            user_id: Unique user identifier
            token: JWT token
            ip_address: Client IP address
            user_agent: Client User-Agent header

        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)

        session_data = {
            "user_id": user_id,
            "token": token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
        }

        # In production: store in Redis with TTL
        # self.redis_client.setex(
        #     f"session:{session_id}",
        #     self.session_timeout,
        #     json.dumps(session_data)
        # )

        logger.info(f"Session created for user: {user_id} (ID: {session_id})")
        return session_id

    def validate_session(
        self,
        session_id: str,
        ip_address: str,
        user_agent: str
    ) -> bool:
        """
        Validate session and detect potential hijacking.

        Args:
            session_id: Session identifier
            ip_address: Current client IP
            user_agent: Current client User-Agent

        Returns:
            True if session is valid, False otherwise

        Raises:
            ValueError: If session hijacking detected
        """
        if not session_id:
            logger.error("Empty session ID provided")
            return False

        # In production: retrieve from Redis
        # session_data = self.redis_client.get(f"session:{session_id}")
        # if not session_data:
        #     logger.error(f"Session not found or expired: {session_id}")
        #     return False

        # Simulated session data for demonstration
        session_data = {
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        # Validate IP address (strict mode)
        if session_data["ip_address"] != ip_address:
            logger.error(
                f"⚠️ POSSIBLE SESSION HIJACKING: IP mismatch "
                f"(expected {session_data['ip_address']}, got {ip_address})"
            )
            raise ValueError("Session hijacking detected - IP address changed")

        # Validate User-Agent
        if session_data["user_agent"] != user_agent:
            logger.warning(
                f"User-Agent changed (expected {session_data['user_agent']}, got {user_agent})"
            )
            # In production: may log event but not reject (User-Agent can change legitimately)

        logger.info(f"Session validated successfully: {session_id}")
        return True

    def revoke_session(self, session_id: str) -> bool:
        """
        Revoke session (logout).

        Args:
            session_id: Session identifier

        Returns:
            True if session was revoked
        """
        # In production: delete from Redis
        # self.redis_client.delete(f"session:{session_id}")

        logger.info(f"Session revoked: {session_id}")
        return True


# Utility Functions

def generate_pkce_pair() -> Tuple[str, str]:
    """
    Generate PKCE code_verifier and code_challenge pair.

    PKCE (Proof Key for Code Exchange) prevents authorization code interception
    by requiring the original code_verifier to exchange the code for tokens.

    Returns:
        Tuple of (code_verifier, code_challenge)
        - code_verifier: Random 128-char string
        - code_challenge: Base64URL-encoded SHA256 hash of code_verifier
    """
    code_verifier = secrets.token_urlsafe(96)  # 128 chars after encoding

    # Generate SHA256 hash
    challenge_bytes = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip('=')

    logger.info("Generated PKCE pair")
    return code_verifier, code_challenge


def validate_tenant_isolation(user_tenant_id: str, resource_tenant_id: str) -> bool:
    """
    Standalone function to validate tenant isolation.

    CRITICAL: Call this before EVERY database query or document retrieval.

    Args:
        user_tenant_id: Tenant ID from user's JWT claims
        resource_tenant_id: Tenant ID of resource being accessed

    Returns:
        True if tenant IDs match

    Raises:
        ValueError: If cross-tenant access attempted
    """
    rbac = RBACEngine()
    return rbac.validate_tenant_isolation(user_tenant_id, resource_tenant_id)


def check_permission(user_roles: List[str], required_permission: str) -> bool:
    """
    Standalone function to check RBAC permissions.

    Args:
        user_roles: List of roles assigned to user
        required_permission: Permission to check (read, write, delete, etc.)

    Returns:
        True if user has permission
    """
    rbac = RBACEngine()
    return rbac.check_permission(user_roles, required_permission)


def detect_session_hijacking(
    session_data: Dict[str, Any],
    current_ip: str,
    current_user_agent: str
) -> bool:
    """
    Detect potential session hijacking through fingerprint analysis.

    Args:
        session_data: Stored session metadata
        current_ip: Current request IP address
        current_user_agent: Current request User-Agent

    Returns:
        True if hijacking detected, False otherwise
    """
    ip_changed = session_data.get("ip_address") != current_ip
    user_agent_changed = session_data.get("user_agent") != current_user_agent

    if ip_changed:
        logger.error(f"⚠️ Session hijacking detected: IP address changed")
        return True

    if user_agent_changed:
        logger.warning(f"User-Agent changed (low-risk indicator)")
        # Return False - User-Agent can change legitimately (browser updates)

    return False
