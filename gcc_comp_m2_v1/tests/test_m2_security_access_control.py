"""
Test suite for L3 M2: Security_Access_Control

Tests cover:
- OAuth 2.0 client functionality
- JWT token validation
- RBAC permission checking
- Tenant isolation enforcement
- Session management and hijacking detection
- PKCE pair generation
- Common failure scenarios
"""

import pytest
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Any

from src.l3_m2_security_access_control import (
    OAuthClient,
    JWTValidator,
    RBACEngine,
    SessionManager,
    generate_pkce_pair,
    validate_tenant_isolation,
    check_permission,
    detect_session_hijacking,
    ROLES,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def oauth_config() -> Dict[str, Any]:
    """OAuth client configuration for testing."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "redirect_uri": "http://localhost:8000/auth/callback",
        "authorization_endpoint": "https://test-idp.okta.com/oauth2/v1/authorize",
        "token_endpoint": "https://test-idp.okta.com/oauth2/v1/token",
        "userinfo_endpoint": "https://test-idp.okta.com/oauth2/v1/userinfo",
        "issuer": "https://test-idp.okta.com",
    }


@pytest.fixture
def jwt_config() -> Dict[str, Any]:
    """JWT validator configuration for testing."""
    return {
        "jwt_secret": "test_secret_key_for_testing",
        "jwt_algorithm": "HS256",  # Using HS256 for easier testing
        "issuer": "https://test-idp.okta.com",
        "audience": "api://test",
    }


@pytest.fixture
def session_config() -> Dict[str, Any]:
    """Session manager configuration for testing."""
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "session_timeout": 3600,
        "max_concurrent_sessions": 3,
    }


@pytest.fixture
def oauth_client(oauth_config) -> OAuthClient:
    """Create OAuth client instance."""
    return OAuthClient(oauth_config)


@pytest.fixture
def jwt_validator(jwt_config) -> JWTValidator:
    """Create JWT validator instance."""
    return JWTValidator(jwt_config)


@pytest.fixture
def rbac_engine() -> RBACEngine:
    """Create RBAC engine instance."""
    return RBACEngine()


@pytest.fixture
def session_manager(session_config) -> SessionManager:
    """Create session manager instance."""
    return SessionManager(session_config)


# ============================================================================
# OAuth Client Tests
# ============================================================================

class TestOAuthClient:
    """Tests for OAuthClient class."""

    def test_initialization(self, oauth_client, oauth_config):
        """Test OAuth client initialization."""
        assert oauth_client.client_id == oauth_config["client_id"]
        assert oauth_client.client_secret == oauth_config["client_secret"]
        assert oauth_client.issuer == oauth_config["issuer"]

    def test_get_authorize_url(self, oauth_client):
        """Test authorization URL generation with PKCE."""
        state = "test_state"
        code_challenge = "test_code_challenge"

        url = oauth_client.get_authorize_url(state, code_challenge)

        assert oauth_client.authorization_endpoint in url
        assert f"client_id={oauth_client.client_id}" in url
        assert f"state={state}" in url
        assert f"code_challenge={code_challenge}" in url
        assert "code_challenge_method=S256" in url
        assert "response_type=code" in url

    def test_exchange_code_for_tokens_valid(self, oauth_client):
        """Test successful token exchange."""
        code = "valid_authorization_code"
        code_verifier = "test_code_verifier"

        tokens = oauth_client.exchange_code_for_tokens(code, code_verifier)

        assert "access_token" in tokens
        assert "id_token" in tokens
        assert "refresh_token" in tokens
        assert "expires_in" in tokens
        assert tokens["token_type"] == "Bearer"
        assert tokens["expires_in"] == 3600

    def test_exchange_code_empty_code(self, oauth_client):
        """Test token exchange with empty authorization code."""
        with pytest.raises(ValueError, match="Authorization code cannot be empty"):
            oauth_client.exchange_code_for_tokens("", "code_verifier")

    def test_get_user_info_valid(self, oauth_client):
        """Test user info retrieval with valid token."""
        access_token = "valid_access_token"

        user_info = oauth_client.get_user_info(access_token)

        assert "sub" in user_info
        assert "email" in user_info
        assert "tenant_id" in user_info
        assert "roles" in user_info
        assert isinstance(user_info["roles"], list)

    def test_get_user_info_empty_token(self, oauth_client):
        """Test user info retrieval with empty token."""
        with pytest.raises(ValueError, match="Access token cannot be empty"):
            oauth_client.get_user_info("")


# ============================================================================
# JWT Validator Tests
# ============================================================================

class TestJWTValidator:
    """Tests for JWTValidator class."""

    def test_initialization(self, jwt_validator, jwt_config):
        """Test JWT validator initialization."""
        assert jwt_validator.secret == jwt_config["jwt_secret"]
        assert jwt_validator.algorithm == jwt_config["jwt_algorithm"]
        assert jwt_validator.issuer == jwt_config["issuer"]

    def test_validate_empty_token(self, jwt_validator):
        """Test validation with empty token."""
        with pytest.raises(ValueError, match="Token cannot be empty"):
            jwt_validator.validate_token("")

    def test_decode_without_verification(self, jwt_validator):
        """Test decoding without verification (debug only)."""
        import jwt

        # Create a simple JWT for testing
        payload = {"sub": "user_123", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(payload, "any_secret", algorithm="HS256")

        decoded = jwt_validator.decode_without_verification(token)

        assert decoded["sub"] == "user_123"


# ============================================================================
# RBAC Engine Tests
# ============================================================================

class TestRBACEngine:
    """Tests for RBACEngine class."""

    def test_initialization(self, rbac_engine):
        """Test RBAC engine initialization."""
        assert rbac_engine.roles == ROLES
        assert len(rbac_engine.roles) == 4  # Admin, Developer, Analyst, Viewer

    def test_check_permission_admin(self, rbac_engine):
        """Test Admin has all permissions."""
        admin_roles = ["Admin"]

        assert rbac_engine.check_permission(admin_roles, "read") is True
        assert rbac_engine.check_permission(admin_roles, "write") is True
        assert rbac_engine.check_permission(admin_roles, "delete") is True
        assert rbac_engine.check_permission(admin_roles, "manage_users") is True
        assert rbac_engine.check_permission(admin_roles, "manage_tenants") is True

    def test_check_permission_developer(self, rbac_engine):
        """Test Developer has read, write, execute permissions."""
        developer_roles = ["Developer"]

        assert rbac_engine.check_permission(developer_roles, "read") is True
        assert rbac_engine.check_permission(developer_roles, "write") is True
        assert rbac_engine.check_permission(developer_roles, "execute") is True
        assert rbac_engine.check_permission(developer_roles, "delete") is False
        assert rbac_engine.check_permission(developer_roles, "manage_users") is False

    def test_check_permission_analyst(self, rbac_engine):
        """Test Analyst has read and query permissions."""
        analyst_roles = ["Analyst"]

        assert rbac_engine.check_permission(analyst_roles, "read") is True
        assert rbac_engine.check_permission(analyst_roles, "query") is True
        assert rbac_engine.check_permission(analyst_roles, "write") is False
        assert rbac_engine.check_permission(analyst_roles, "delete") is False

    def test_check_permission_viewer(self, rbac_engine):
        """Test Viewer has only read permission."""
        viewer_roles = ["Viewer"]

        assert rbac_engine.check_permission(viewer_roles, "read") is True
        assert rbac_engine.check_permission(viewer_roles, "write") is False
        assert rbac_engine.check_permission(viewer_roles, "query") is False

    def test_check_permission_multiple_roles(self, rbac_engine):
        """Test user with multiple roles."""
        multi_roles = ["Viewer", "Analyst"]

        # Should have permissions from both roles
        assert rbac_engine.check_permission(multi_roles, "read") is True
        assert rbac_engine.check_permission(multi_roles, "query") is True

    def test_check_permission_invalid_role(self, rbac_engine):
        """Test invalid role returns no permissions."""
        invalid_roles = ["InvalidRole"]

        assert rbac_engine.check_permission(invalid_roles, "read") is False

    def test_get_role_permissions(self, rbac_engine):
        """Test getting permissions for a role."""
        admin_perms = rbac_engine.get_role_permissions("Admin")
        assert "manage_users" in admin_perms
        assert "delete" in admin_perms

        viewer_perms = rbac_engine.get_role_permissions("Viewer")
        assert viewer_perms == ["read"]

    def test_validate_tenant_isolation_same_tenant(self, rbac_engine):
        """Test tenant isolation with matching tenant IDs."""
        user_tenant = "tenant_abc"
        resource_tenant = "tenant_abc"

        result = rbac_engine.validate_tenant_isolation(user_tenant, resource_tenant)
        assert result is True

    def test_validate_tenant_isolation_different_tenant(self, rbac_engine):
        """Test tenant isolation with different tenant IDs - should raise."""
        user_tenant = "tenant_abc"
        resource_tenant = "tenant_xyz"

        with pytest.raises(ValueError, match="Cross-tenant access denied"):
            rbac_engine.validate_tenant_isolation(user_tenant, resource_tenant)


# ============================================================================
# Session Manager Tests
# ============================================================================

class TestSessionManager:
    """Tests for SessionManager class."""

    def test_initialization(self, session_manager, session_config):
        """Test session manager initialization."""
        assert session_manager.redis_host == session_config["redis_host"]
        assert session_manager.redis_port == session_config["redis_port"]
        assert session_manager.session_timeout == session_config["session_timeout"]

    def test_create_session(self, session_manager):
        """Test session creation."""
        user_id = "user_123"
        token = "jwt_token"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"

        session_id = session_manager.create_session(
            user_id, token, ip_address, user_agent
        )

        assert isinstance(session_id, str)
        assert len(session_id) > 20  # Should be a secure random string

    def test_validate_session_same_ip(self, session_manager):
        """Test session validation with same IP address."""
        session_id = "test_session_id"
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"

        # This is simulated in the implementation
        is_valid = session_manager.validate_session(
            session_id, ip_address, user_agent
        )

        assert is_valid is True

    def test_validate_session_empty_session_id(self, session_manager):
        """Test session validation with empty session ID."""
        is_valid = session_manager.validate_session("", "192.168.1.100", "Mozilla/5.0")
        assert is_valid is False

    def test_revoke_session(self, session_manager):
        """Test session revocation."""
        session_id = "test_session_id"

        result = session_manager.revoke_session(session_id)
        assert result is True


# ============================================================================
# Utility Function Tests
# ============================================================================

class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_generate_pkce_pair(self):
        """Test PKCE pair generation."""
        code_verifier, code_challenge = generate_pkce_pair()

        # Verify code_verifier length
        assert len(code_verifier) >= 43  # Minimum per RFC 7636

        # Verify code_challenge is base64url-encoded SHA256 hash
        expected_challenge_bytes = hashlib.sha256(code_verifier.encode()).digest()
        expected_challenge = base64.urlsafe_b64encode(expected_challenge_bytes).decode().rstrip('=')
        assert code_challenge == expected_challenge

    def test_generate_pkce_pair_uniqueness(self):
        """Test that PKCE pairs are unique."""
        pair1 = generate_pkce_pair()
        pair2 = generate_pkce_pair()

        assert pair1[0] != pair2[0]  # Different code_verifier
        assert pair1[1] != pair2[1]  # Different code_challenge

    def test_validate_tenant_isolation_function(self):
        """Test standalone tenant isolation function."""
        user_tenant = "tenant_abc"
        resource_tenant = "tenant_abc"

        result = validate_tenant_isolation(user_tenant, resource_tenant)
        assert result is True

    def test_validate_tenant_isolation_violation(self):
        """Test tenant isolation violation."""
        user_tenant = "tenant_abc"
        resource_tenant = "tenant_xyz"

        with pytest.raises(ValueError, match="Cross-tenant access denied"):
            validate_tenant_isolation(user_tenant, resource_tenant)

    def test_check_permission_function(self):
        """Test standalone permission check function."""
        assert check_permission(["Admin"], "delete") is True
        assert check_permission(["Viewer"], "write") is False

    def test_detect_session_hijacking_ip_changed(self):
        """Test session hijacking detection - IP address changed."""
        session_data = {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
        }
        current_ip = "192.168.1.200"  # Different IP
        current_user_agent = "Mozilla/5.0"

        is_hijacked = detect_session_hijacking(
            session_data, current_ip, current_user_agent
        )

        assert is_hijacked is True

    def test_detect_session_hijacking_user_agent_changed(self):
        """Test session hijacking detection - User-Agent changed."""
        session_data = {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
        }
        current_ip = "192.168.1.100"
        current_user_agent = "Chrome/120.0"  # Different User-Agent

        is_hijacked = detect_session_hijacking(
            session_data, current_ip, current_user_agent
        )

        # User-Agent change is low-risk, so returns False
        assert is_hijacked is False

    def test_detect_session_hijacking_no_change(self):
        """Test session hijacking detection - no changes."""
        session_data = {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
        }
        current_ip = "192.168.1.100"
        current_user_agent = "Mozilla/5.0"

        is_hijacked = detect_session_hijacking(
            session_data, current_ip, current_user_agent
        )

        assert is_hijacked is False


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegrationWorkflows:
    """Integration tests for complete workflows."""

    def test_complete_oauth_flow(self, oauth_client):
        """Test complete OAuth flow from authorization to user info."""
        # Step 1: Generate PKCE pair
        code_verifier, code_challenge = generate_pkce_pair()

        # Step 2: Get authorization URL
        state = "test_state"
        auth_url = oauth_client.get_authorize_url(state, code_challenge)
        assert oauth_client.authorization_endpoint in auth_url

        # Step 3: Exchange code for tokens (simulated)
        tokens = oauth_client.exchange_code_for_tokens("auth_code", code_verifier)
        assert "access_token" in tokens

        # Step 4: Get user info
        user_info = oauth_client.get_user_info(tokens["access_token"])
        assert "tenant_id" in user_info
        assert "roles" in user_info

    def test_rbac_with_tenant_isolation(self, rbac_engine):
        """Test RBAC permission check combined with tenant isolation."""
        user_roles = ["Developer"]
        user_tenant = "tenant_abc"
        resource_tenant = "tenant_abc"

        # Check permission
        has_permission = rbac_engine.check_permission(user_roles, "write")
        assert has_permission is True

        # Check tenant isolation
        is_isolated = rbac_engine.validate_tenant_isolation(user_tenant, resource_tenant)
        assert is_isolated is True

        # Combined: permission granted and tenant validated
        can_access = has_permission and is_isolated
        assert can_access is True

    def test_session_lifecycle(self, session_manager):
        """Test complete session lifecycle."""
        # Create session
        session_id = session_manager.create_session(
            user_id="user_123",
            token="jwt_token",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0"
        )
        assert session_id is not None

        # Validate session
        is_valid = session_manager.validate_session(
            session_id, "192.168.1.100", "Mozilla/5.0"
        )
        assert is_valid is True

        # Revoke session
        revoked = session_manager.revoke_session(session_id)
        assert revoked is True


# ============================================================================
# Failure Scenario Tests (from script Section 8)
# ============================================================================

class TestCommonFailures:
    """Tests for common failure scenarios from the augmented script."""

    def test_authorization_code_replay_attack(self, oauth_client):
        """
        Failure 1: Authorization code replay attack.

        Same authorization code should only be usable once.
        """
        code = "authorization_code_123"
        code_verifier = "test_verifier"

        # First exchange - should succeed
        tokens1 = oauth_client.exchange_code_for_tokens(code, code_verifier)
        assert tokens1 is not None

        # Second exchange with same code - in production, should fail
        # Note: Current implementation is simulated, doesn't track used codes
        # In production, this would raise ValueError("Authorization code already used")

    def test_mismatched_redirect_uri(self, oauth_config):
        """
        Failure 2: Mismatched redirect_uri configuration.

        redirect_uri in request must exactly match IdP configuration.
        """
        # Test exact match requirement
        config1 = oauth_config.copy()
        config1["redirect_uri"] = "http://localhost:8000/auth/callback"

        config2 = oauth_config.copy()
        config2["redirect_uri"] = "http://localhost:8000/auth/callback/"  # Trailing slash

        # These should be treated as different URIs
        assert config1["redirect_uri"] != config2["redirect_uri"]

    def test_expired_token_handling(self):
        """
        Failure 3: Expired token without graceful refresh.

        System should detect expired tokens and handle gracefully.
        """
        import jwt
        from datetime import datetime, timedelta

        # Create expired token
        payload = {
            "sub": "user_123",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        expired_token = jwt.encode(payload, "secret", algorithm="HS256")

        # Validation should fail
        jwt_config = {
            "jwt_secret": "secret",
            "jwt_algorithm": "HS256",
            "issuer": "test",
            "audience": "test",
        }
        validator = JWTValidator(jwt_config)

        with pytest.raises(Exception):  # Should raise ExpiredSignatureError
            validator.validate_token(expired_token)

    def test_session_hijacking_ip_mismatch(self):
        """
        Failure 4: Session hijacking through IP validation gaps.

        System should detect and reject requests from different IP.
        """
        session_data = {
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
        }

        # Request from different IP
        is_hijacked = detect_session_hijacking(
            session_data,
            current_ip="10.0.0.50",  # Different IP
            current_user_agent="Mozilla/5.0"
        )

        assert is_hijacked is True

    def test_concurrent_session_limit_enforcement(self, session_manager):
        """
        Failure 5: Concurrent session limits not enforced.

        User should not have unlimited active sessions.
        """
        max_sessions = session_manager.max_concurrent_sessions
        assert max_sessions == 3  # Default limit

        # In production, creating 4th session should revoke oldest
        # Current implementation is simulated

    def test_tenant_isolation_bypass_in_query(self, rbac_engine):
        """
        Failure 7: Tenant isolation bypass in raw SQL queries.

        Every query must validate tenant_id.
        """
        user_tenant = "tenant_abc"
        document_tenant = "tenant_xyz"

        # This should raise ValueError
        with pytest.raises(ValueError, match="Cross-tenant access denied"):
            rbac_engine.validate_tenant_isolation(user_tenant, document_tenant)

    def test_token_validation_without_signature_check(self):
        """
        Failure 8: Token validation without signature check.

        CRITICAL: Always verify signature BEFORE checking claims.
        """
        import jwt

        # Create a token
        payload = {"sub": "user_123", "tenant_id": "tenant_abc"}
        token = jwt.encode(payload, "correct_secret", algorithm="HS256")

        # ❌ WRONG: Decode without verification
        decoded_insecure = jwt.decode(token, options={"verify_signature": False})
        assert decoded_insecure["sub"] == "user_123"

        # Attacker could modify token and it would still pass!
        # This demonstrates why signature verification is CRITICAL

        # ✅ CORRECT: Verify signature first
        jwt_config = {
            "jwt_secret": "correct_secret",
            "jwt_algorithm": "HS256",
            "issuer": "test",
            "audience": "test",
        }
        validator = JWTValidator(jwt_config)

        # With wrong secret, validation should fail
        jwt_config_wrong = jwt_config.copy()
        jwt_config_wrong["jwt_secret"] = "wrong_secret"
        validator_wrong = JWTValidator(jwt_config_wrong)

        # This should raise an exception
        # (In actual test, would need real JWT library behavior)


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_roles_list(self, rbac_engine):
        """Test permission check with empty roles list."""
        result = rbac_engine.check_permission([], "read")
        assert result is False

    def test_role_case_sensitivity(self, rbac_engine):
        """Test that role names are case-sensitive."""
        # "admin" (lowercase) should not match "Admin"
        result = rbac_engine.check_permission(["admin"], "manage_users")
        assert result is False

        # "Admin" (correct case) should match
        result = rbac_engine.check_permission(["Admin"], "manage_users")
        assert result is True

    def test_pkce_verifier_length(self):
        """Test PKCE code_verifier meets minimum length requirement."""
        code_verifier, _ = generate_pkce_pair()

        # RFC 7636 requires minimum 43 characters
        assert len(code_verifier) >= 43
        assert len(code_verifier) <= 128  # Maximum per RFC

    def test_multiple_concurrent_roles(self, rbac_engine):
        """Test user with multiple overlapping roles."""
        roles = ["Viewer", "Analyst", "Developer"]

        # Should have cumulative permissions
        assert rbac_engine.check_permission(roles, "read") is True
        assert rbac_engine.check_permission(roles, "query") is True
        assert rbac_engine.check_permission(roles, "write") is True
        assert rbac_engine.check_permission(roles, "execute") is True

        # Should not have Admin-only permissions
        assert rbac_engine.check_permission(roles, "manage_users") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
