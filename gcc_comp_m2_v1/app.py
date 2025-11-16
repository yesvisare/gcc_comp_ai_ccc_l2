"""
FastAPI application for L3 M2: Security_Access_Control

Exposes OAuth 2.0 authentication endpoints with JWT validation,
RBAC enforcement, and session management for multi-tenant RAG systems.
"""

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
import secrets

from src.l3_m2_security_access_control import (
    OAuthClient,
    JWTValidator,
    RBACEngine,
    SessionManager,
    generate_pkce_pair,
    validate_tenant_isolation,
    check_permission,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="L3 M2: Security_Access_Control",
    description="Authentication & Identity Management for Multi-Tenant RAG Systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated configuration (in production, load from config.py)
OAUTH_CONFIG = {
    "client_id": "demo_client_id",
    "client_secret": "demo_client_secret",
    "redirect_uri": "http://localhost:8000/auth/callback",
    "authorization_endpoint": "https://your-idp.okta.com/oauth2/v1/authorize",
    "token_endpoint": "https://your-idp.okta.com/oauth2/v1/token",
    "userinfo_endpoint": "https://your-idp.okta.com/oauth2/v1/userinfo",
    "issuer": "https://your-idp.okta.com",
}

JWT_CONFIG = {
    "jwt_secret": "your_jwt_secret_key_here",
    "jwt_algorithm": "RS256",
    "issuer": "https://your-idp.okta.com",
    "audience": "api://default",
}

SESSION_CONFIG = {
    "redis_host": "localhost",
    "redis_port": 6379,
    "session_timeout": 3600,
    "max_concurrent_sessions": 3,
}

# Initialize components
oauth_client = OAuthClient(OAUTH_CONFIG)
jwt_validator = JWTValidator(JWT_CONFIG)
rbac_engine = RBACEngine()
session_manager = SessionManager(SESSION_CONFIG)

# Temporary storage for PKCE verifiers (in production: use Redis)
pkce_storage = {}


# Pydantic Models

class LoginResponse(BaseModel):
    """Response model for login initiation."""
    authorize_url: str
    state: str


class TokenExchangeRequest(BaseModel):
    """Request model for token exchange."""
    code: str = Field(..., description="Authorization code from IdP callback")
    state: str = Field(..., description="State parameter for CSRF protection")


class TokenResponse(BaseModel):
    """Response model for successful token exchange."""
    access_token: str
    id_token: str
    refresh_token: str
    expires_in: int
    token_type: str


class UserInfoResponse(BaseModel):
    """Response model for user information."""
    sub: str
    email: str
    name: str
    tenant_id: str
    roles: List[str]
    email_verified: bool
    mfa_enabled: bool


class PermissionCheckRequest(BaseModel):
    """Request model for permission check."""
    roles: List[str] = Field(..., description="User roles")
    permission: str = Field(..., description="Required permission (read, write, delete, etc.)")


class TenantIsolationRequest(BaseModel):
    """Request model for tenant isolation validation."""
    user_tenant_id: str = Field(..., description="Tenant ID from user's JWT")
    resource_tenant_id: str = Field(..., description="Tenant ID of resource being accessed")


class LogoutRequest(BaseModel):
    """Request model for logout."""
    session_id: str = Field(..., description="Session ID to revoke")


# Endpoints

@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Status information about the service
    """
    return {
        "status": "healthy",
        "service": "l3_m2_security_access_control",
        "version": "1.0.0",
        "oauth_configured": bool(OAUTH_CONFIG.get("client_id")),
    }


@app.get("/auth/login", response_model=LoginResponse)
async def initiate_login():
    """
    Initiate OAuth 2.0 login flow with PKCE.

    This endpoint:
    1. Generates PKCE code_verifier and code_challenge
    2. Creates random state parameter for CSRF protection
    3. Returns authorization URL to redirect user to IdP

    Returns:
        LoginResponse with authorize_url and state
    """
    try:
        # Generate PKCE pair
        code_verifier, code_challenge = generate_pkce_pair()

        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store code_verifier temporarily (in production: use Redis)
        pkce_storage[state] = code_verifier

        # Generate authorization URL
        authorize_url = oauth_client.get_authorize_url(state, code_challenge)

        logger.info(f"Login initiated with state: {state}")

        return LoginResponse(
            authorize_url=authorize_url,
            state=state
        )

    except Exception as e:
        logger.error(f"Login initiation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate login")


@app.get("/auth/callback")
async def oauth_callback(code: str, state: str):
    """
    OAuth callback handler - receives authorization code from IdP.

    This endpoint:
    1. Validates state parameter (CSRF protection)
    2. Retrieves code_verifier from storage
    3. Exchanges authorization code for tokens
    4. Creates session with security fingerprints

    Args:
        code: Authorization code from IdP
        state: State parameter for validation

    Returns:
        Redirect to frontend with tokens or session ID
    """
    try:
        # Validate state (CSRF protection)
        code_verifier = pkce_storage.get(state)
        if not code_verifier:
            logger.error(f"Invalid state parameter: {state}")
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        # Exchange code for tokens
        tokens = oauth_client.exchange_code_for_tokens(code, code_verifier)

        # Clean up PKCE storage
        del pkce_storage[state]

        logger.info("OAuth callback processed successfully")

        # In production: create session and redirect to frontend
        return JSONResponse({
            "success": True,
            "message": "Authentication successful",
            "tokens": tokens
        })

    except ValueError as e:
        logger.error(f"Token exchange failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Callback processing failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@app.post("/auth/exchange", response_model=TokenResponse)
async def exchange_token(request: TokenExchangeRequest):
    """
    Exchange authorization code for tokens (alternative to callback).

    Args:
        request: TokenExchangeRequest with code and state

    Returns:
        TokenResponse with access_token, id_token, refresh_token
    """
    try:
        # Validate state
        code_verifier = pkce_storage.get(request.state)
        if not code_verifier:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        # Exchange code for tokens
        tokens = oauth_client.exchange_code_for_tokens(request.code, code_verifier)

        # Clean up
        del pkce_storage[request.state]

        return TokenResponse(**tokens)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        raise HTTPException(status_code=500, detail="Token exchange failed")


@app.get("/auth/userinfo", response_model=UserInfoResponse)
async def get_user_info(authorization: str = Header(...)):
    """
    Get current user information from access token.

    Args:
        authorization: Bearer token in Authorization header

    Returns:
        UserInfoResponse with user profile and claims
    """
    try:
        # Extract token from "Bearer <token>"
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        access_token = authorization.split(" ")[1]

        # Get user info from IdP
        user_info = oauth_client.get_user_info(access_token)

        return UserInfoResponse(**user_info)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user information")


@app.post("/auth/validate-token")
async def validate_jwt_token(authorization: str = Header(...)):
    """
    Validate JWT token signature and claims.

    Args:
        authorization: Bearer token in Authorization header

    Returns:
        Decoded JWT payload with claims
    """
    try:
        # Extract token
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization.split(" ")[1]

        # Validate token
        payload = jwt_validator.validate_token(token)

        return {
            "valid": True,
            "payload": payload
        }

    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.post("/rbac/check-permission")
async def check_rbac_permission(request: PermissionCheckRequest):
    """
    Check if user roles grant required permission.

    Args:
        request: PermissionCheckRequest with roles and permission

    Returns:
        Boolean indicating if permission is granted
    """
    try:
        has_permission = check_permission(request.roles, request.permission)

        return {
            "has_permission": has_permission,
            "roles": request.roles,
            "permission": request.permission,
        }

    except Exception as e:
        logger.error(f"Permission check failed: {e}")
        raise HTTPException(status_code=500, detail="Permission check failed")


@app.get("/rbac/roles")
async def get_all_roles():
    """
    Get all available roles and their permissions.

    Returns:
        Dictionary of roles and permissions
    """
    from src.l3_m2_security_access_control import ROLES
    return {
        "roles": ROLES,
        "description": "Standard RBAC roles with permission inheritance"
    }


@app.post("/tenant/validate-isolation")
async def validate_tenant_access(request: TenantIsolationRequest):
    """
    Validate tenant isolation for cross-tenant access prevention.

    CRITICAL: Call this before every database query or document retrieval.

    Args:
        request: TenantIsolationRequest with user and resource tenant IDs

    Returns:
        Validation result
    """
    try:
        is_valid = validate_tenant_isolation(
            request.user_tenant_id,
            request.resource_tenant_id
        )

        return {
            "valid": is_valid,
            "user_tenant_id": request.user_tenant_id,
            "resource_tenant_id": request.resource_tenant_id,
            "message": "Tenant isolation validated successfully"
        }

    except ValueError as e:
        logger.error(f"Tenant isolation violation: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Tenant validation failed: {e}")
        raise HTTPException(status_code=500, detail="Tenant validation failed")


@app.post("/session/create")
async def create_session(
    request: Request,
    user_id: str,
    token: str,
):
    """
    Create new session with security fingerprints.

    Args:
        user_id: User identifier
        token: JWT token
        request: FastAPI request (for IP and User-Agent extraction)

    Returns:
        Session ID
    """
    try:
        # Extract security fingerprints
        ip_address = request.client.host
        user_agent = request.headers.get("User-Agent", "")

        # Create session
        session_id = session_manager.create_session(
            user_id=user_id,
            token=token,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return {
            "session_id": session_id,
            "user_id": user_id,
            "expires_in": SESSION_CONFIG["session_timeout"],
        }

    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@app.post("/session/validate")
async def validate_session(
    request: Request,
    session_id: str,
):
    """
    Validate session and detect potential hijacking.

    Args:
        session_id: Session identifier
        request: FastAPI request (for IP and User-Agent extraction)

    Returns:
        Validation result
    """
    try:
        # Extract current fingerprints
        ip_address = request.client.host
        user_agent = request.headers.get("User-Agent", "")

        # Validate session
        is_valid = session_manager.validate_session(
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return {
            "valid": is_valid,
            "session_id": session_id,
            "message": "Session validated successfully"
        }

    except ValueError as e:
        logger.error(f"Session validation failed: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        raise HTTPException(status_code=500, detail="Session validation failed")


@app.post("/auth/logout")
async def logout(request: LogoutRequest):
    """
    Logout user and revoke session.

    Args:
        request: LogoutRequest with session_id

    Returns:
        Logout confirmation
    """
    try:
        success = session_manager.revoke_session(request.session_id)

        return {
            "success": success,
            "message": "Logout successful"
        }

    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")


# Development endpoint - remove in production
@app.get("/dev/pkce-demo")
async def demo_pkce():
    """
    Demonstrate PKCE pair generation (development only).

    Returns:
        Example PKCE code_verifier and code_challenge
    """
    code_verifier, code_challenge = generate_pkce_pair()

    return {
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "note": "In production, code_verifier is stored securely and never exposed"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
