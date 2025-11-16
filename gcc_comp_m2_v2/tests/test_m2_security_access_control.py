"""
Test suite for L3 M2.2: Authorization & Multi-Tenant Access Control

Tests cover:
- RBAC permission checks
- Cross-tenant access denial
- Namespace isolation
- ABAC policy evaluation
- Audit trail verification
- JWT token validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.l3_m2_security_access_control import (
    AuthorizationManager,
    NamespaceManager,
    AuditLogger,
    query_with_authorization,
    validate_jwt_token,
    check_rbac_permission,
    evaluate_abac_policy,
    create_audit_log_entry,
)


# Fixtures


@pytest.fixture
def sample_config():
    """Fixture providing test configuration."""
    return {
        "pinecone_enabled": False,
        "postgres_enabled": False,
        "opa_enabled": False,
    }


@pytest.fixture
def mock_pinecone_client():
    """Mock Pinecone client."""
    client = Mock()
    client.query = Mock(return_value={"matches": []})
    return client


@pytest.fixture
def mock_opa_client():
    """Mock OPA client."""
    return {
        "url": "http://localhost:8181",
        "client": Mock(),
    }


@pytest.fixture
def auth_manager(mock_pinecone_client):
    """AuthorizationManager instance for testing."""
    return AuthorizationManager(
        pinecone_client=mock_pinecone_client,
        db_engine=None,
        opa_client=None,
    )


@pytest.fixture
def namespace_manager(mock_pinecone_client):
    """NamespaceManager instance for testing."""
    return NamespaceManager(
        pinecone_client=mock_pinecone_client,
        db_engine=None,
    )


@pytest.fixture
def audit_logger():
    """AuditLogger instance for testing."""
    return AuditLogger(db_engine=None)


# RBAC Permission Tests


def test_admin_full_access():
    """Test that admin role has access to all namespaces."""
    result = check_rbac_permission(
        user_role="admin",
        user_namespace="admin-prod",
        target_namespace="finance-prod",
    )
    assert result["allowed"] is True
    assert "Admin" in result["reason"]


def test_analyst_same_namespace_access():
    """Test that analyst can access their assigned namespace."""
    result = check_rbac_permission(
        user_role="analyst",
        user_namespace="finance-prod",
        target_namespace="finance-prod",
    )
    assert result["allowed"] is True
    assert "assigned namespace" in result["reason"]


def test_analyst_cross_tenant_denial():
    """Test that analyst cannot access other namespaces (zero cross-tenant leakage)."""
    result = check_rbac_permission(
        user_role="analyst",
        user_namespace="finance-prod",
        target_namespace="hr-prod",
    )
    assert result["allowed"] is False
    assert "Cross-tenant access denied" in result["reason"]
    assert "finance-prod -> hr-prod" in result["reason"]


def test_compliance_officer_read_all():
    """Test that compliance officer has read access to all namespaces."""
    result = check_rbac_permission(
        user_role="compliance_officer",
        user_namespace="audit-prod",
        target_namespace="legal-prod",
    )
    assert result["allowed"] is True
    assert "Compliance Officer" in result["reason"]


def test_unknown_role_denial():
    """Test that unknown roles are denied by default."""
    result = check_rbac_permission(
        user_role="unknown_role",
        user_namespace="test-prod",
        target_namespace="test-prod",
    )
    assert result["allowed"] is False
    assert "Unknown role" in result["reason"]


# Authorization Manager Tests


def test_authorization_manager_initialization(auth_manager):
    """Test AuthorizationManager initializes correctly."""
    assert auth_manager.pinecone_client is not None
    assert auth_manager.db_engine is None
    assert auth_manager.opa_client is None


def test_authorize_query_rbac_allow(auth_manager):
    """Test successful authorization with RBAC."""
    result = auth_manager.authorize_query(
        user_id="alice@company.com",
        user_role="admin",
        user_namespace="admin-prod",
        target_namespace="finance-prod",
        query="Show revenue",
    )
    assert result["authorized"] is True
    assert result["policy_used"] == "RBAC"


def test_authorize_query_rbac_deny(auth_manager):
    """Test authorization denial with RBAC."""
    result = auth_manager.authorize_query(
        user_id="bob@company.com",
        user_role="analyst",
        user_namespace="hr-prod",
        target_namespace="finance-prod",
        query="Show revenue",
    )
    assert result["authorized"] is False
    assert "Cross-tenant" in result["reason"]


@patch('src.l3_m2_security_access_control.evaluate_abac_policy')
def test_authorize_query_abac_integration(mock_abac, mock_opa_client):
    """Test authorization with ABAC policy evaluation."""
    # Mock ABAC to deny
    mock_abac.return_value = {"allowed": False, "reason": "Location not allowed"}

    auth_manager = AuthorizationManager(
        pinecone_client=None,
        db_engine=None,
        opa_client=mock_opa_client,
    )

    result = auth_manager.authorize_query(
        user_id="alice@company.com",
        user_role="admin",
        user_namespace="admin-prod",
        target_namespace="finance-prod",
        query="Show revenue",
        context={"location": "CN"},
    )

    assert result["authorized"] is False
    assert "Location not allowed" in result["reason"]
    assert result["policy_used"] == "ABAC"


# Namespace Manager Tests


def test_namespace_creation(namespace_manager):
    """Test namespace creation."""
    result = namespace_manager.create_namespace(
        namespace="finance-prod",
        business_unit="Finance",
        region="US",
    )
    assert result["namespace"] == "finance-prod"
    assert result["business_unit"] == "Finance"
    assert result["region"] == "US"
    assert result["status"] == "created"


def test_list_namespaces_admin(namespace_manager):
    """Test that admin can list all namespaces."""
    namespaces = namespace_manager.list_user_namespaces(
        user_id="admin@company.com",
        user_role="admin",
    )
    assert len(namespaces) > 0
    assert "finance-prod" in namespaces
    assert "hr-prod" in namespaces


def test_list_namespaces_analyst(namespace_manager):
    """Test that analyst only sees assigned namespace."""
    namespaces = namespace_manager.list_user_namespaces(
        user_id="analyst@company.com",
        user_role="analyst",
    )
    assert len(namespaces) >= 1
    # In production, this would query database for user's assigned namespace


def test_list_namespaces_compliance_officer(namespace_manager):
    """Test that compliance officer can list all namespaces."""
    namespaces = namespace_manager.list_user_namespaces(
        user_id="compliance@company.com",
        user_role="compliance_officer",
    )
    assert len(namespaces) > 0


# Audit Logger Tests


def test_audit_log_creation(audit_logger):
    """Test audit log entry creation."""
    log_entry = audit_logger.log_access_attempt(
        user_id="alice@company.com",
        action="query",
        namespace="finance-prod",
        resources_accessed=["doc1", "doc2"],
        decision="allowed",
        policy_used="RBAC",
    )
    assert log_entry["user_id"] == "alice@company.com"
    assert log_entry["action"] == "query"
    assert log_entry["namespace"] == "finance-prod"
    assert log_entry["decision"] == "allowed"
    assert log_entry["policy_used"] == "RBAC"
    assert "timestamp" in log_entry


def test_audit_log_denial(audit_logger):
    """Test audit log for denied access."""
    log_entry = audit_logger.log_access_attempt(
        user_id="bob@company.com",
        action="query",
        namespace="hr-prod",
        decision="denied",
        policy_used="RBAC",
    )
    assert log_entry["decision"] == "denied"


def test_create_audit_log_entry():
    """Test standalone audit log creation function."""
    entry = create_audit_log_entry(
        user_id="test@company.com",
        action="create_namespace",
        namespace="test-prod",
        decision="allowed",
        policy_used="RBAC",
        resources=["namespace:test-prod"],
    )
    assert entry["user_id"] == "test@company.com"
    assert entry["action"] == "create_namespace"
    assert "timestamp" in entry


# ABAC Policy Tests


@patch('src.l3_m2_security_access_control.requests.post')
def test_abac_policy_allow(mock_post):
    """Test ABAC policy evaluation - allowed."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": True}
    mock_post.return_value = mock_response

    opa_client = {"url": "http://localhost:8181", "client": Mock()}

    result = evaluate_abac_policy(
        user_id="alice@company.com",
        user_role="analyst",
        target_namespace="finance-prod",
        context={"location": "US", "classification": "internal"},
        opa_client=opa_client,
    )

    assert result["allowed"] is True
    assert "ABAC policy allowed" in result["reason"]


@patch('src.l3_m2_security_access_control.requests.post')
def test_abac_policy_deny(mock_post):
    """Test ABAC policy evaluation - denied."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": False}
    mock_post.return_value = mock_response

    opa_client = {"url": "http://localhost:8181", "client": Mock()}

    result = evaluate_abac_policy(
        user_id="alice@company.com",
        user_role="analyst",
        target_namespace="finance-prod",
        context={"location": "CN", "classification": "confidential"},
        opa_client=opa_client,
    )

    assert result["allowed"] is False
    assert "ABAC policy denied" in result["reason"]


@patch('src.l3_m2_security_access_control.requests.post')
def test_abac_policy_opa_unavailable(mock_post):
    """Test ABAC policy when OPA is unavailable (fail-safe denial)."""
    mock_post.side_effect = Exception("Connection refused")

    opa_client = {"url": "http://localhost:8181", "client": Mock()}

    result = evaluate_abac_policy(
        user_id="alice@company.com",
        user_role="analyst",
        target_namespace="finance-prod",
        context={},
        opa_client=opa_client,
    )

    assert result["allowed"] is False
    assert "error" in result["reason"].lower()


# Query with Authorization Tests


def test_query_with_authorization_success():
    """Test successful query with authorization."""
    result = query_with_authorization(
        query="Show revenue",
        user_id="alice@company.com",
        user_role="admin",
        user_namespace="admin-prod",
        target_namespace="finance-prod",
        pinecone_client=None,  # Will use mock results
        opa_client=None,
    )
    assert result["status"] == "success"
    assert "results" in result
    assert "audit_log" in result


def test_query_with_authorization_rbac_denial():
    """Test query denial due to RBAC."""
    result = query_with_authorization(
        query="Show revenue",
        user_id="bob@company.com",
        user_role="analyst",
        user_namespace="hr-prod",
        target_namespace="finance-prod",
        pinecone_client=None,
        opa_client=None,
    )
    assert result["status"] == "denied"
    assert "Cross-tenant" in result["reason"]
    assert "audit_log" in result


def test_query_with_authorization_default_namespace():
    """Test query with default namespace (user's own)."""
    result = query_with_authorization(
        query="Show policies",
        user_id="carol@company.com",
        user_role="analyst",
        user_namespace="hr-prod",
        # No target_namespace - should default to user_namespace
        pinecone_client=None,
        opa_client=None,
    )
    assert result["status"] == "success"
    assert result["results"]["namespace"] == "hr-prod"


# JWT Token Tests


@patch('src.l3_m2_security_access_control.jwt')
def test_validate_jwt_token_success(mock_jwt):
    """Test successful JWT token validation."""
    mock_jwt.decode.return_value = {
        "sub": "alice@company.com",
        "role": "admin",
        "namespace": "admin-prod",
    }

    claims = validate_jwt_token("valid.token.here", "secret-key")

    assert claims["sub"] == "alice@company.com"
    assert claims["role"] == "admin"
    mock_jwt.decode.assert_called_once()


@patch('src.l3_m2_security_access_control.jwt')
def test_validate_jwt_token_expired(mock_jwt):
    """Test JWT token validation with expired token."""
    import jwt as pyjwt

    mock_jwt.decode.side_effect = pyjwt.ExpiredSignatureError("Token expired")
    mock_jwt.ExpiredSignatureError = pyjwt.ExpiredSignatureError

    with pytest.raises(Exception, match="Token expired"):
        validate_jwt_token("expired.token.here", "secret-key")


@patch('src.l3_m2_security_access_control.jwt')
def test_validate_jwt_token_invalid(mock_jwt):
    """Test JWT token validation with invalid token."""
    import jwt as pyjwt

    mock_jwt.decode.side_effect = pyjwt.InvalidTokenError("Invalid token")
    mock_jwt.InvalidTokenError = pyjwt.InvalidTokenError

    with pytest.raises(Exception, match="Invalid token"):
        validate_jwt_token("invalid.token.here", "secret-key")


# Integration Tests


def test_end_to_end_authorized_query():
    """Test complete flow: authorization + query + audit."""
    # Simulate admin querying finance namespace
    result = query_with_authorization(
        query="Q3 revenue projections",
        user_id="admin@company.com",
        user_role="admin",
        user_namespace="admin-prod",
        target_namespace="finance-prod",
        context={"location": "US"},
        pinecone_client=None,
        opa_client=None,
    )

    assert result["status"] == "success"
    assert result["results"]["namespace"] == "finance-prod"
    assert result["audit_log"]["decision"] == "allowed"
    assert result["audit_log"]["user_id"] == "admin@company.com"


def test_end_to_end_denied_query():
    """Test complete flow: authorization denial + audit."""
    # Simulate analyst trying to access different namespace
    result = query_with_authorization(
        query="Show employee records",
        user_id="analyst@company.com",
        user_role="analyst",
        user_namespace="finance-prod",
        target_namespace="hr-prod",
        pinecone_client=None,
        opa_client=None,
    )

    assert result["status"] == "denied"
    assert result["audit_log"]["decision"] == "denied"
    assert "Cross-tenant" in result["reason"]


def test_compliance_officer_cross_namespace_access():
    """Test that compliance officer can access multiple namespaces."""
    # Test access to finance
    result1 = query_with_authorization(
        query="Show finance audit trail",
        user_id="compliance@company.com",
        user_role="compliance_officer",
        user_namespace="audit-prod",
        target_namespace="finance-prod",
        pinecone_client=None,
        opa_client=None,
    )

    # Test access to hr
    result2 = query_with_authorization(
        query="Show hr audit trail",
        user_id="compliance@company.com",
        user_role="compliance_officer",
        user_namespace="audit-prod",
        target_namespace="hr-prod",
        pinecone_client=None,
        opa_client=None,
    )

    assert result1["status"] == "success"
    assert result2["status"] == "success"


# Performance and Security Tests


def test_namespace_isolation_enforcement():
    """Test that namespace isolation is enforced at query level."""
    result = query_with_authorization(
        query="test query",
        user_id="analyst@company.com",
        user_role="analyst",
        user_namespace="finance-prod",
        target_namespace="finance-prod",
        pinecone_client=None,
        opa_client=None,
    )

    # Verify namespace is enforced in results
    assert result["results"]["namespace"] == "finance-prod"


def test_audit_log_immutability():
    """Test that audit logs are created with timestamp (immutable in production)."""
    audit_logger = AuditLogger()

    log1 = audit_logger.log_access_attempt(
        user_id="test@company.com",
        action="query",
        namespace="test-prod",
        decision="allowed",
        policy_used="RBAC",
    )

    # In production, timestamp ensures write-once (no UPDATE/DELETE)
    assert "timestamp" in log1
    assert log1["decision"] == "allowed"


# Parametrized Tests for Multiple Scenarios


@pytest.mark.parametrize(
    "role,user_ns,target_ns,expected",
    [
        ("admin", "admin-prod", "finance-prod", True),
        ("admin", "admin-prod", "hr-prod", True),
        ("analyst", "finance-prod", "finance-prod", True),
        ("analyst", "finance-prod", "hr-prod", False),
        ("compliance_officer", "audit-prod", "finance-prod", True),
        ("compliance_officer", "audit-prod", "legal-prod", True),
    ],
)
def test_rbac_matrix(role, user_ns, target_ns, expected):
    """Test RBAC permission matrix for all role combinations."""
    result = check_rbac_permission(
        user_role=role,
        user_namespace=user_ns,
        target_namespace=target_ns,
    )
    assert result["allowed"] == expected
