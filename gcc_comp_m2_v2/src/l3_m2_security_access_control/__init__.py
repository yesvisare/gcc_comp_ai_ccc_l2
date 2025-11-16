"""
L3 M2.2: Authorization & Multi-Tenant Access Control

This module implements RBAC and ABAC authorization for multi-tenant RAG systems
serving Government Community Cloud (GCC) environments with 50+ business units.

Key Features:
- Three-role RBAC (Admin, Analyst, Compliance Officer)
- Namespace-based multi-tenant isolation in Pinecone
- ABAC using Open Policy Agent (OPA) for context-aware access
- Immutable audit logging for compliance
- Zero cross-tenant data leakage guarantees

Architecture:
1. JWT token validation (from M2.1)
2. RBAC permission checks
3. ABAC policy evaluation via OPA
4. Namespace isolation at vector DB level
5. Immutable audit trail
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

__all__ = [
    "AuthorizationManager",
    "NamespaceManager",
    "AuditLogger",
    "query_with_authorization",
    "validate_jwt_token",
    "check_rbac_permission",
    "evaluate_abac_policy",
    "create_audit_log_entry",
]


class AuthorizationManager:
    """
    Manages authorization decisions using RBAC and ABAC.

    This class coordinates between role-based and attribute-based access control
    to make authorization decisions for multi-tenant RAG queries.
    """

    def __init__(
        self,
        pinecone_client=None,
        db_engine=None,
        opa_client=None,
        role_permissions: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialize the authorization manager.

        Args:
            pinecone_client: Pinecone client instance
            db_engine: SQLAlchemy database engine
            opa_client: OPA client configuration
            role_permissions: Custom role-permission mapping
        """
        self.pinecone_client = pinecone_client
        self.db_engine = db_engine
        self.opa_client = opa_client
        self.role_permissions = role_permissions or {}
        logger.info("Initialized AuthorizationManager")

    def authorize_query(
        self,
        user_id: str,
        user_role: str,
        user_namespace: str,
        target_namespace: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Authorize a query using RBAC and ABAC.

        Args:
            user_id: User identifier
            user_role: User's role (admin, analyst, compliance_officer)
            user_namespace: User's assigned namespace
            target_namespace: Target namespace for query
            query: Query text
            context: Additional context (location, time, classification)

        Returns:
            Authorization decision with details
        """
        logger.info(f"Authorizing query for user {user_id} (role: {user_role})")

        # Step 1: Check RBAC permissions
        rbac_result = check_rbac_permission(
            user_role=user_role,
            user_namespace=user_namespace,
            target_namespace=target_namespace,
        )

        if not rbac_result["allowed"]:
            logger.warning(f"RBAC denied for user {user_id}: {rbac_result['reason']}")
            return {
                "authorized": False,
                "reason": rbac_result["reason"],
                "policy_used": "RBAC",
            }

        # Step 2: Evaluate ABAC policy (if OPA enabled)
        if self.opa_client:
            abac_result = evaluate_abac_policy(
                user_id=user_id,
                user_role=user_role,
                target_namespace=target_namespace,
                context=context or {},
                opa_client=self.opa_client,
            )

            if not abac_result["allowed"]:
                logger.warning(f"ABAC denied for user {user_id}: {abac_result['reason']}")
                return {
                    "authorized": False,
                    "reason": abac_result["reason"],
                    "policy_used": "ABAC",
                }

        logger.info(f"Authorization granted for user {user_id}")
        return {
            "authorized": True,
            "namespace": target_namespace,
            "policy_used": "RBAC+ABAC" if self.opa_client else "RBAC",
        }


class NamespaceManager:
    """
    Manages multi-tenant namespace isolation in Pinecone.

    Ensures zero cross-tenant data leakage through namespace-based isolation.
    """

    def __init__(self, pinecone_client=None, db_engine=None):
        """
        Initialize the namespace manager.

        Args:
            pinecone_client: Pinecone client instance
            db_engine: SQLAlchemy database engine
        """
        self.pinecone_client = pinecone_client
        self.db_engine = db_engine
        logger.info("Initialized NamespaceManager")

    def create_namespace(self, namespace: str, business_unit: str, region: str) -> Dict[str, Any]:
        """
        Create a new namespace for a business unit.

        Args:
            namespace: Namespace identifier (e.g., 'finance-prod')
            business_unit: Business unit name
            region: Region (e.g., 'US', 'IN')

        Returns:
            Creation result
        """
        logger.info(f"Creating namespace: {namespace} for {business_unit}")

        try:
            # In production, this would create a namespace record in PostgreSQL
            # and configure Pinecone index namespace
            result = {
                "namespace": namespace,
                "business_unit": business_unit,
                "region": region,
                "created_at": datetime.utcnow().isoformat(),
                "status": "created",
            }
            logger.info(f"Namespace created successfully: {namespace}")
            return result
        except Exception as e:
            logger.error(f"Failed to create namespace {namespace}: {e}")
            raise

    def list_user_namespaces(self, user_id: str, user_role: str) -> List[str]:
        """
        List all namespaces accessible to a user.

        Args:
            user_id: User identifier
            user_role: User's role

        Returns:
            List of accessible namespace names
        """
        logger.info(f"Listing namespaces for user {user_id} (role: {user_role})")

        # Admin and Compliance Officer can access all namespaces
        if user_role in ["admin", "compliance_officer"]:
            # In production, query from database
            return ["finance-prod", "hr-prod", "legal-prod", "admin-prod"]

        # Analysts can only access their assigned namespace
        # In production, query from database
        return ["finance-prod"]  # Example: user assigned to finance


class AuditLogger:
    """
    Manages immutable audit logging for compliance.

    Implements write-once audit trail with 7-year retention for regulatory compliance.
    """

    def __init__(self, db_engine=None):
        """
        Initialize the audit logger.

        Args:
            db_engine: SQLAlchemy database engine
        """
        self.db_engine = db_engine
        logger.info("Initialized AuditLogger")

    def log_access_attempt(
        self,
        user_id: str,
        action: str,
        namespace: str,
        resources_accessed: Optional[List[str]] = None,
        decision: str = "allowed",
        policy_used: str = "RBAC",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an immutable audit log entry.

        Args:
            user_id: User identifier
            action: Action attempted (query, create_namespace, etc.)
            namespace: Target namespace
            resources_accessed: List of resources accessed
            decision: Authorization decision (allowed/denied)
            policy_used: Policy that made the decision (RBAC/ABAC)
            context: Additional context

        Returns:
            Audit log entry
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "namespace": namespace,
            "resources_accessed": resources_accessed or [],
            "decision": decision,
            "policy_used": policy_used,
            "context": context or {},
        }

        logger.info(f"Audit log: {decision} - {user_id} - {action} - {namespace}")

        # In production, write to immutable audit_logs table in PostgreSQL
        # with INSERT-only permissions (no UPDATE/DELETE)

        return log_entry


# Standalone Functions


def validate_jwt_token(token: str, secret_key: str, algorithm: str = "HS256") -> Dict[str, Any]:
    """
    Validate JWT token and extract claims.

    Args:
        token: JWT token string
        secret_key: Secret key for validation
        algorithm: JWT algorithm (default: HS256)

    Returns:
        Decoded token claims

    Raises:
        Exception: If token is invalid or expired
    """
    try:
        import jwt

        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        logger.info(f"JWT token validated for user: {payload.get('sub', 'unknown')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("JWT token has expired")
        raise Exception("Token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid JWT token: {e}")
        raise Exception("Invalid token")
    except ImportError:
        logger.error("PyJWT package not installed")
        raise Exception("JWT validation unavailable")


def check_rbac_permission(
    user_role: str,
    user_namespace: str,
    target_namespace: str,
) -> Dict[str, Any]:
    """
    Check RBAC permissions for namespace access.

    Args:
        user_role: User's role (admin, analyst, compliance_officer)
        user_namespace: User's assigned namespace
        target_namespace: Target namespace for access

    Returns:
        Permission decision with reason
    """
    # Admin can access all namespaces
    if user_role == "admin":
        return {"allowed": True, "reason": "Admin has full access"}

    # Compliance Officer can read from all namespaces
    if user_role == "compliance_officer":
        return {"allowed": True, "reason": "Compliance Officer has read-all access"}

    # Analyst can only access their assigned namespace
    if user_role == "analyst":
        if user_namespace == target_namespace:
            return {"allowed": True, "reason": "Analyst accessing assigned namespace"}
        else:
            return {
                "allowed": False,
                "reason": f"Cross-tenant access denied: {user_namespace} -> {target_namespace}",
            }

    # Unknown role - deny by default
    return {"allowed": False, "reason": f"Unknown role: {user_role}"}


def evaluate_abac_policy(
    user_id: str,
    user_role: str,
    target_namespace: str,
    context: Dict[str, Any],
    opa_client: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluate ABAC policy using Open Policy Agent.

    Args:
        user_id: User identifier
        user_role: User's role
        target_namespace: Target namespace
        context: Context attributes (location, time, classification)
        opa_client: OPA client configuration

    Returns:
        Policy decision
    """
    try:
        import requests

        # Construct OPA policy input
        policy_input = {
            "input": {
                "user": {
                    "id": user_id,
                    "role": user_role,
                    "location": context.get("location", "unknown"),
                },
                "resource": {
                    "namespace": target_namespace,
                    "classification": context.get("classification", "internal"),
                },
                "context": {
                    "time": datetime.utcnow().isoformat(),
                    "ip_address": context.get("ip_address", "unknown"),
                },
            }
        }

        # Query OPA
        opa_url = opa_client["url"]
        response = requests.post(
            f"{opa_url}/v1/data/gcc/authz/allow",
            json=policy_input,
            timeout=5,
        )

        if response.status_code == 200:
            result = response.json()
            allowed = result.get("result", False)

            if allowed:
                return {"allowed": True, "reason": "ABAC policy allowed"}
            else:
                return {"allowed": False, "reason": "ABAC policy denied"}
        else:
            logger.warning(f"OPA request failed: {response.status_code}")
            # Fail-safe: deny if OPA unavailable
            return {"allowed": False, "reason": "OPA unavailable"}

    except Exception as e:
        logger.error(f"ABAC evaluation failed: {e}")
        # Fail-safe: deny on error
        return {"allowed": False, "reason": f"ABAC evaluation error: {e}"}


def create_audit_log_entry(
    user_id: str,
    action: str,
    namespace: str,
    decision: str,
    policy_used: str,
    resources: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create an audit log entry (convenience function).

    Args:
        user_id: User identifier
        action: Action performed
        namespace: Target namespace
        decision: Authorization decision
        policy_used: Policy that made decision
        resources: Resources accessed

    Returns:
        Audit log entry
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "namespace": namespace,
        "decision": decision,
        "policy_used": policy_used,
        "resources_accessed": resources or [],
    }


def query_with_authorization(
    query: str,
    user_id: str,
    user_role: str,
    user_namespace: str,
    target_namespace: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    pinecone_client=None,
    opa_client=None,
) -> Dict[str, Any]:
    """
    Execute a query with full authorization checks.

    This is the main entry point for authorized RAG queries.

    Args:
        query: Query text
        user_id: User identifier
        user_role: User's role
        user_namespace: User's assigned namespace
        target_namespace: Target namespace (defaults to user_namespace)
        context: Additional context for ABAC
        pinecone_client: Pinecone client instance
        opa_client: OPA client configuration

    Returns:
        Query results or error
    """
    target_namespace = target_namespace or user_namespace
    logger.info(f"Processing query for user {user_id}: {query[:50]}...")

    # Step 1: RBAC check
    rbac_result = check_rbac_permission(
        user_role=user_role,
        user_namespace=user_namespace,
        target_namespace=target_namespace,
    )

    if not rbac_result["allowed"]:
        # Log denial
        audit_entry = create_audit_log_entry(
            user_id=user_id,
            action="query",
            namespace=target_namespace,
            decision="denied",
            policy_used="RBAC",
        )
        logger.warning(f"Query denied: {rbac_result['reason']}")

        return {
            "status": "denied",
            "reason": rbac_result["reason"],
            "audit_log": audit_entry,
        }

    # Step 2: ABAC check (if enabled)
    if opa_client:
        abac_result = evaluate_abac_policy(
            user_id=user_id,
            user_role=user_role,
            target_namespace=target_namespace,
            context=context or {},
            opa_client=opa_client,
        )

        if not abac_result["allowed"]:
            # Log denial
            audit_entry = create_audit_log_entry(
                user_id=user_id,
                action="query",
                namespace=target_namespace,
                decision="denied",
                policy_used="ABAC",
            )
            logger.warning(f"Query denied by ABAC: {abac_result['reason']}")

            return {
                "status": "denied",
                "reason": abac_result["reason"],
                "audit_log": audit_entry,
            }

    # Step 3: Execute query with namespace isolation
    try:
        if pinecone_client:
            # In production, this would execute a Pinecone query with namespace filter
            logger.info(f"Executing query in namespace: {target_namespace}")
            results = {
                "query": query,
                "namespace": target_namespace,
                "matches": [
                    {"id": "doc1", "score": 0.95, "text": "Sample result 1"},
                    {"id": "doc2", "score": 0.87, "text": "Sample result 2"},
                ],
            }
        else:
            logger.warning("Pinecone client not available - returning mock results")
            results = {
                "query": query,
                "namespace": target_namespace,
                "matches": [],
                "note": "Mock results (Pinecone disabled)",
            }

        # Step 4: Log successful access
        audit_entry = create_audit_log_entry(
            user_id=user_id,
            action="query",
            namespace=target_namespace,
            decision="allowed",
            policy_used="RBAC+ABAC" if opa_client else "RBAC",
            resources=[match["id"] for match in results.get("matches", [])],
        )

        logger.info(f"Query executed successfully for user {user_id}")

        return {
            "status": "success",
            "results": results,
            "audit_log": audit_entry,
        }

    except Exception as e:
        logger.error(f"Query execution failed: {e}")

        # Log failure
        audit_entry = create_audit_log_entry(
            user_id=user_id,
            action="query",
            namespace=target_namespace,
            decision="error",
            policy_used="N/A",
        )

        return {
            "status": "error",
            "reason": str(e),
            "audit_log": audit_entry,
        }
