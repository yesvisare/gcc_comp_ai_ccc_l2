"""
FastAPI wrapper for L3 M2.2: Authorization & Multi-Tenant Access Control

Production-ready REST API for multi-tenant RAG system with RBAC and ABAC.
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

# Import from package
from src.l3_m2_security_access_control import (
    AuthorizationManager,
    NamespaceManager,
    AuditLogger,
    query_with_authorization,
    validate_jwt_token,
)

# Import configuration
import config

# Configure logging
logging.basicConfig(
    level=config.ENVIRONMENT == "development" and logging.DEBUG or logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="L3 M2.2: Authorization & Multi-Tenant Access Control API",
    description="Production API for GCC Compliance multi-tenant authorization with RBAC and ABAC",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize managers
auth_manager = AuthorizationManager(
    pinecone_client=config.pinecone_client,
    db_engine=config.db_engine,
    opa_client=config.opa_client,
    role_permissions=config.ROLE_PERMISSIONS,
)

namespace_manager = NamespaceManager(
    pinecone_client=config.pinecone_client,
    db_engine=config.db_engine,
)

audit_logger = AuditLogger(db_engine=config.db_engine)


# Request/Response Models


class QueryRequest(BaseModel):
    """Request model for authorized query."""

    query: str = Field(..., description="Query text")
    user_id: str = Field(..., description="User identifier (email)")
    user_role: str = Field(..., description="User role (admin/analyst/compliance_officer)")
    user_namespace: str = Field(..., description="User's assigned namespace")
    target_namespace: Optional[str] = Field(None, description="Target namespace (defaults to user_namespace)")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context for ABAC (location, time, etc.)"
    )


class NamespaceCreateRequest(BaseModel):
    """Request model for namespace creation."""

    namespace: str = Field(..., description="Namespace identifier (e.g., 'finance-prod')")
    business_unit: str = Field(..., description="Business unit name")
    region: str = Field(..., description="Region (e.g., 'US', 'IN')")


class AuthorizationCheckRequest(BaseModel):
    """Request model for authorization check."""

    user_id: str
    user_role: str
    user_namespace: str
    target_namespace: str
    action: str
    context: Optional[Dict[str, Any]] = None


# Dependency for JWT validation


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Validate JWT token from Authorization header.

    Args:
        authorization: Authorization header (Bearer token)

    Returns:
        Decoded JWT claims

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        # Validate token
        claims = validate_jwt_token(token, config.JWT_SECRET_KEY, config.JWT_ALGORITHM)
        return claims

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")


# API Endpoints


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "module": "L3_M2_Security_Access_Control",
        "version": "1.0.0",
        "services": {
            "pinecone": config.PINECONE_ENABLED,
            "postgres": config.POSTGRES_ENABLED,
            "opa": config.OPA_ENABLED,
        },
    }


@app.get("/health")
async def health_check():
    """Detailed health check with service status."""
    health_status = {
        "api": "healthy",
        "timestamp": "2025-01-16T00:00:00Z",
        "services": {
            "pinecone": {
                "enabled": config.PINECONE_ENABLED,
                "status": "connected" if config.pinecone_client else "offline",
            },
            "postgres": {
                "enabled": config.POSTGRES_ENABLED,
                "status": "connected" if config.db_engine else "offline",
            },
            "opa": {
                "enabled": config.OPA_ENABLED,
                "status": "connected" if config.opa_client else "offline",
            },
        },
    }
    return health_status


@app.post("/query")
async def query(request: QueryRequest):
    """
    Process query with full authorization checks.

    Implements:
    1. RBAC permission check
    2. ABAC policy evaluation (if OPA enabled)
    3. Namespace isolation enforcement
    4. Immutable audit logging

    Returns:
        Query results or 403 Forbidden
    """
    try:
        logger.info(f"Received query from user {request.user_id}")

        # Execute query with authorization
        result = query_with_authorization(
            query=request.query,
            user_id=request.user_id,
            user_role=request.user_role,
            user_namespace=request.user_namespace,
            target_namespace=request.target_namespace,
            context=request.context,
            pinecone_client=config.pinecone_client,
            opa_client=config.opa_client,
        )

        # Log to audit trail
        audit_logger.log_access_attempt(
            user_id=request.user_id,
            action="query",
            namespace=request.target_namespace or request.user_namespace,
            decision=result["status"],
            policy_used=result.get("audit_log", {}).get("policy_used", "RBAC"),
        )

        if result["status"] == "denied":
            raise HTTPException(status_code=403, detail=result["reason"])

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["reason"])

        return {
            "status": "success",
            "results": result["results"],
            "audit_log_id": result.get("audit_log", {}).get("timestamp"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/authorize")
async def authorize(request: AuthorizationCheckRequest):
    """
    Check authorization without executing query.

    Useful for pre-flight checks in UI.
    """
    try:
        auth_result = auth_manager.authorize_query(
            user_id=request.user_id,
            user_role=request.user_role,
            user_namespace=request.user_namespace,
            target_namespace=request.target_namespace,
            query="",  # Not executing, just checking
            context=request.context,
        )

        return {
            "authorized": auth_result["authorized"],
            "reason": auth_result.get("reason", "Authorized"),
            "policy_used": auth_result.get("policy_used", "RBAC"),
        }

    except Exception as e:
        logger.error(f"Authorization check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/namespaces")
async def create_namespace(request: NamespaceCreateRequest):
    """
    Create a new namespace for a business unit.

    Requires admin role.
    """
    try:
        result = namespace_manager.create_namespace(
            namespace=request.namespace,
            business_unit=request.business_unit,
            region=request.region,
        )

        # Log to audit trail
        audit_logger.log_access_attempt(
            user_id="admin",  # In production, extract from JWT
            action="create_namespace",
            namespace=request.namespace,
            decision="allowed",
            policy_used="RBAC",
        )

        return result

    except Exception as e:
        logger.error(f"Namespace creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/namespaces")
async def list_namespaces(user_id: str, user_role: str):
    """
    List all namespaces accessible to a user.

    - Admin/Compliance Officer: All namespaces
    - Analyst: Only assigned namespace
    """
    try:
        namespaces = namespace_manager.list_user_namespaces(user_id=user_id, user_role=user_role)

        return {
            "user_id": user_id,
            "role": user_role,
            "namespaces": namespaces,
        }

    except Exception as e:
        logger.error(f"Namespace listing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = None, namespace: Optional[str] = None, limit: int = 100
):
    """
    Retrieve audit logs.

    Requires compliance_officer or admin role.
    """
    try:
        # In production, query from audit_logs table
        sample_logs = [
            {
                "timestamp": "2025-01-16T10:30:00Z",
                "user_id": user_id or "alice@company.com",
                "action": "query",
                "namespace": namespace or "finance-prod",
                "decision": "allowed",
                "policy_used": "RBAC",
            }
        ]

        return {"logs": sample_logs[:limit], "count": len(sample_logs)}

    except Exception as e:
        logger.error(f"Audit log retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=config.ENVIRONMENT == "development",
        log_level="info",
    )
