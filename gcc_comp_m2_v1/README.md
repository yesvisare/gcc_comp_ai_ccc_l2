# L3 M2: Security_Access_Control — Authentication & Identity Management

> **Production-ready** OAuth 2.0 / OIDC authentication system with multi-tenant isolation for GCC RAG environments serving 50+ business units in regulated industries.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This module implements enterprise-grade authentication and identity management for multi-tenant RAG systems in regulated industries (healthcare, finance, government). It addresses the critical security challenge of preventing cross-tenant data leakage while enabling Single Sign-On (SSO) integration with corporate Identity Providers.

**Real-World Context:** A GCC system serving 50+ business units without proper authentication controls experienced cross-tenant data leaks, failed SOC 2 audit, and lost a $3.2M contract. This module provides the foundational security layer to prevent such failures.

**Key Capabilities:**
- OAuth 2.0 / OIDC integration with enterprise Identity Providers (Okta, Azure AD, Auth0, Google Workspace)
- JWT token validation with cryptographic signature verification (RS256/HS256)
- Role-Based Access Control (RBAC) with four standard roles and permission inheritance
- Multi-tenant isolation with namespace-based filtering (`user.tenant_id == document.tenant_id`)
- Session management using Redis-backed token storage with configurable TTL
- Multi-Factor Authentication (MFA) enforcement with TOTP and hardware token support
- Session hijacking prevention through IP address and User-Agent validation
- Audit trail logging for SOC 2 / regulatory compliance

## Learning Outcomes

By completing this module, you will:

1. **Implement OAuth 2.0/OIDC authentication flow** with enterprise Identity Providers (Okta, Azure AD) using authorization code flow with PKCE
2. **Design RBAC systems** with multi-tenant awareness, four standard roles (Admin, Developer, Analyst, Viewer), and permission inheritance
3. **Configure MFA enforcement** with TOTP codes and hardware token support for privileged operations
4. **Build session management** with Redis-backed token storage, TTL matching JWT expiration, and concurrent session limits
5. **Prevent session hijacking** through IP validation, User-Agent fingerprinting, and secure session metadata
6. **Validate JWT tokens** with signature verification (check signature BEFORE claims), expiration handling, and issuer/audience validation
7. **Enforce tenant isolation** at the query level to prevent cross-tenant data leakage in multi-tenant environments

## Concepts Covered

### 1. Authentication vs. Authorization

**Authentication** answers "Who are you?" — verifying user identity through credentials, tokens, or biometrics.

**Authorization** answers "What can you do?" — determining permissions after identity is established.

**Critical Distinction:** Authentication must happen BEFORE authorization. Never check permissions without validating identity first.

**Example Flow:**
```
User Login → Authenticate (verify identity) → Issue JWT token
User Request → Validate JWT (re-authenticate) → Check RBAC (authorize) → Allow/Deny
```

### 2. OAuth 2.0 and OpenID Connect (OIDC)

**OAuth 2.0** is a delegated authorization framework that allows third-party applications to access user resources without exposing passwords.

**OIDC** extends OAuth 2.0 to add authentication, providing identity tokens (ID tokens) alongside access tokens.

**Authorization Code Flow with PKCE:**
1. User clicks "Login with Okta"
2. System redirects to Identity Provider with `code_challenge` (SHA256 hash)
3. User authenticates at IdP
4. IdP redirects back with authorization `code`
5. System exchanges `code` + `code_verifier` for tokens (server-to-server)
6. JWT token issued to user

**PKCE (Proof Key for Code Exchange)** prevents authorization code interception attacks by requiring the original `code_verifier` to exchange the code.

**Standard OIDC Scopes:**
- `openid` (required) — Enables OIDC authentication
- `profile` — User attributes (name, picture)
- `email` — Email address (often used as unique identifier)

### 3. JWT (JSON Web Tokens)

JWT tokens are cryptographically signed identity assertions containing claims about the user.

**Structure:** `header.payload.signature`
- **Header:** Algorithm (RS256/HS256) and token type
- **Payload:** Claims (sub, tenant_id, roles, exp, iss, aud)
- **Signature:** Cryptographic proof of authenticity

**Validation Order (CRITICAL):**
1. **Signature verification** (MUST be first — never trust unverified tokens!)
2. Expiration check (`exp` claim)
3. Not-before check (`nbf` claim)
4. Issuer validation (`iss` claim)
5. Audience validation (`aud` claim)

**Example JWT Payload:**
```json
{
  "sub": "user_12345",
  "email": "john.doe@example.com",
  "tenant_id": "tenant_abc",
  "roles": ["Developer"],
  "exp": 1735689600,
  "iss": "https://your-idp.okta.com",
  "aud": "api://default"
}
```

### 4. Role-Based Access Control (RBAC)

RBAC assigns permissions to roles, then assigns roles to users, enabling scalable permission management.

**Four Standard Roles:**

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | read, write, delete, manage_users, manage_tenants | System administrators |
| **Developer** | read, write, execute | Engineers building on the platform |
| **Analyst** | read, query | Business analysts running reports |
| **Viewer** | read | Read-only stakeholders |

**Permission Inheritance:** Roles can inherit permissions (e.g., Developer inherits Viewer permissions).

**Multi-Tenant RBAC:** Every permission check MUST include tenant isolation:
```python
# ❌ WRONG - no tenant check
if check_permission(user.roles, "read"):
    return query_documents()

# ✅ CORRECT - enforce tenant isolation
if check_permission(user.roles, "read") and user.tenant_id == document.tenant_id:
    return query_documents()
```

### 5. Multi-Tenancy and Tenant Isolation

**Multi-tenancy** allows a single system to serve multiple independent customers (tenants) with data isolation.

**Tenant Isolation Strategies:**
- **Namespace-based:** Each tenant has a unique `tenant_id` prefix on all resources
- **Database-level:** Separate database per tenant (high isolation, high cost)
- **Row-level security:** PostgreSQL RLS policies enforce tenant filtering

**CRITICAL Rule:** Every query must validate `user.tenant_id == document.tenant_id` to prevent cross-tenant leakage.

**Example Failure Scenario:**
```python
# User from tenant_abc requests document from tenant_xyz
# WITHOUT validation → SECURITY BREACH (cross-tenant data leak)
# WITH validation → 403 Forbidden
```

### 6. Multi-Factor Authentication (MFA)

MFA requires multiple authentication factors:
- **Something you know:** Password
- **Something you have:** TOTP code (Google Authenticator), hardware token (YubiKey)
- **Something you are:** Biometrics (fingerprint, face recognition)

**TOTP (Time-Based One-Time Password):** Generates 6-digit codes that expire every 30 seconds, synchronized between server and authenticator app.

**MFA Enforcement Patterns:**
- **Always required:** All users must configure MFA
- **Role-based:** Only Admin/Developer roles require MFA
- **Risk-based:** MFA triggered by suspicious activity (new device, unusual location)

### 7. Session Management and Security

**Session Components:**
- **Session ID:** Unique identifier stored in cookie or header
- **Session Store:** Redis with TTL matching JWT expiration
- **Security Fingerprints:** IP address, User-Agent for hijacking detection

**Session Hijacking Prevention:**
1. **IP Validation:** Reject requests from different IP than session creation
2. **User-Agent Validation:** Log warnings if User-Agent changes (can change legitimately)
3. **Concurrent Session Limits:** Max 3 active sessions per user
4. **Automatic Expiration:** Redis TTL automatically revokes expired sessions

**Session Lifecycle:**
```
Login → Create session (store IP, User-Agent)
Request → Validate session (check IP match, update activity timestamp)
Logout → Revoke session (delete from Redis)
Timeout → Automatic expiration (Redis TTL)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Enterprise Identity Provider (Okta / Azure AD / Auth0)      │
│  • OAuth 2.0 Authorization Server                           │
│  • OIDC UserInfo Endpoint                                   │
│  • MFA Enforcement                                          │
└───────────────────────────┬─────────────────────────────────┘
                            │ OAuth 2.0 / OIDC
                            │ (Authorization Code + PKCE)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Authentication Middleware (FastAPI)                         │
│  ├── Token Validation (JWT signature + claims)             │
│  ├── RBAC Policy Engine (4 roles, permission inheritance)  │
│  └── Tenant Isolation Enforcement                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐
│ Redis Cache  │  │ PostgreSQL DB    │  │ RAG System      │
│ • Session    │  │ • Users          │  │ • Retrieval     │
│   Storage    │  │ • Tenants        │  │ • Generation    │
│ • Token TTL  │  │ • Audit Logs     │  │ • Multi-tenant  │
└──────────────┘  └──────────────────┘  └─────────────────┘
```

**Component Responsibilities:**

1. **Identity Provider:** Handles user authentication, MFA enforcement, SSO integration with corporate directory
2. **OAuth Client:** Initiates login flow, exchanges authorization codes for tokens, retrieves user profile
3. **JWT Validator:** Verifies token signatures, validates claims (exp, iss, aud), rejects expired/invalid tokens
4. **RBAC Engine:** Checks user roles against required permissions, enforces tenant isolation on every query
5. **Session Manager:** Creates sessions with security fingerprints, detects hijacking attempts, manages concurrent sessions
6. **Redis:** Stores session metadata with automatic expiration (TTL), provides fast session lookup
7. **PostgreSQL:** Stores user/tenant metadata, audit logs for compliance, RBAC role assignments

## Installation

### Prerequisites

- Python 3.10+
- Docker (for Redis and PostgreSQL)
- OAuth application registered with Identity Provider (Okta, Azure AD, Auth0, etc.)

### Step 1: Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd gcc_comp_m2_v1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Infrastructure

```bash
# Start Redis (session storage)
docker run -d -p 6379:6379 --name gcc-redis redis:7-alpine

# Start PostgreSQL (user/tenant metadata)
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=gcc_user \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=gcc_auth_db \
  --name gcc-postgres postgres:15
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your OAuth credentials
# Minimum required:
#   - OAUTH_CLIENT_ID
#   - OAUTH_CLIENT_SECRET
#   - OAUTH_AUTHORIZATION_ENDPOINT
#   - OAUTH_TOKEN_ENDPOINT
#   - OAUTH_ISSUER
#   - JWT_SECRET_KEY
#   - SESSION_SECRET_KEY
```

**Generate Secure Keys:**
```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate session secret
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Step 4: Verify Configuration

```bash
# Validate configuration
python config.py

# Expected output:
# ✓ OAuth configuration validated
# ✓ JWT configuration validated
# ✓ Session configuration validated
```

## Quick Start

### 1. Start API Server

**Option A: PowerShell (Windows)**
```powershell
.\scripts\run_api.ps1
```

**Option B: Direct uvicorn**
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Visit API documentation: http://localhost:8000/docs

### 2. Run Jupyter Notebook

```bash
jupyter notebook notebooks/L3_M2_Security_Access_Control.ipynb
```

The notebook provides an interactive walkthrough of all authentication concepts with live examples.

### 3. Run Tests

**Option A: PowerShell (Windows)**
```powershell
.\scripts\run_tests.ps1
```

**Option B: Direct pytest**
```bash
pytest tests/ -v
```

## Usage Examples

### Example 1: OAuth Login Flow

```python
from src.l3_m2_security_access_control import OAuthClient, generate_pkce_pair

# Initialize OAuth client
oauth_config = {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "redirect_uri": "http://localhost:8000/auth/callback",
    "authorization_endpoint": "https://your-idp.okta.com/oauth2/v1/authorize",
    "token_endpoint": "https://your-idp.okta.com/oauth2/v1/token",
    "userinfo_endpoint": "https://your-idp.okta.com/oauth2/v1/userinfo",
    "issuer": "https://your-idp.okta.com",
}

client = OAuthClient(oauth_config)

# Generate PKCE pair
code_verifier, code_challenge = generate_pkce_pair()

# Get authorization URL
state = "random_state_for_csrf_protection"
auth_url = client.get_authorize_url(state, code_challenge)

# User redirects to auth_url, authenticates at IdP...
# IdP redirects back with authorization code

# Exchange code for tokens
tokens = client.exchange_code_for_tokens(
    authorization_code="code_from_idp_callback",
    code_verifier=code_verifier
)

print(f"Access Token: {tokens['access_token']}")
print(f"Expires in: {tokens['expires_in']} seconds")
```

### Example 2: JWT Token Validation

```python
from src.l3_m2_security_access_control import JWTValidator

# Initialize validator
jwt_config = {
    "jwt_secret": "your_jwt_secret_or_public_key",
    "jwt_algorithm": "RS256",
    "issuer": "https://your-idp.okta.com",
    "audience": "api://default",
}

validator = JWTValidator(jwt_config)

# Validate token
try:
    payload = validator.validate_token(token)
    print(f"Valid token for user: {payload['sub']}")
    print(f"Tenant ID: {payload['tenant_id']}")
    print(f"Roles: {payload['roles']}")
except Exception as e:
    print(f"Invalid token: {e}")
```

### Example 3: RBAC Permission Check

```python
from src.l3_m2_security_access_control import check_permission

# Check if user has write permission
user_roles = ["Developer"]
has_write = check_permission(user_roles, "write")

if has_write:
    print("User can write documents")
else:
    print("Access denied - insufficient permissions")

# Admin has all permissions
admin_roles = ["Admin"]
print(check_permission(admin_roles, "manage_users"))  # True
print(check_permission(admin_roles, "delete"))  # True

# Viewer has only read
viewer_roles = ["Viewer"]
print(check_permission(viewer_roles, "read"))  # True
print(check_permission(viewer_roles, "write"))  # False
```

### Example 4: Tenant Isolation Validation

```python
from src.l3_m2_security_access_control import validate_tenant_isolation

# Extract from JWT token
user_tenant_id = "tenant_abc"
document_tenant_id = "tenant_abc"

try:
    # CRITICAL: Call before every database query
    validate_tenant_isolation(user_tenant_id, document_tenant_id)
    print("✓ Tenant isolation validated - query allowed")

    # Safe to query documents
    results = query_documents(tenant_id=user_tenant_id)

except ValueError as e:
    print(f"⚠️ Cross-tenant access denied: {e}")
    # Log security event, return 403 Forbidden
```

### Example 5: Session Management

```python
from src.l3_m2_security_access_control import SessionManager

# Initialize session manager
session_config = {
    "redis_host": "localhost",
    "redis_port": 6379,
    "session_timeout": 3600,
    "max_concurrent_sessions": 3,
}

manager = SessionManager(session_config)

# Create session on login
session_id = manager.create_session(
    user_id="user_12345",
    token="jwt_token_here",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0 ..."
)

# Validate session on subsequent requests
try:
    is_valid = manager.validate_session(
        session_id=session_id,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 ..."
    )
    print("✓ Session valid")
except ValueError as e:
    print(f"⚠️ Session hijacking detected: {e}")
    # Force re-authentication

# Logout
manager.revoke_session(session_id)
```

## API Endpoints

### Authentication Endpoints

#### `GET /auth/login`
Initiate OAuth 2.0 login flow with PKCE.

**Response:**
```json
{
  "authorize_url": "https://idp.okta.com/oauth2/v1/authorize?...",
  "state": "random_state_string"
}
```

**Usage:** Redirect user to `authorize_url`

---

#### `GET /auth/callback?code={code}&state={state}`
OAuth callback handler - receives authorization code from IdP.

**Parameters:**
- `code`: Authorization code from IdP
- `state`: CSRF protection token

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "tokens": {
    "access_token": "...",
    "id_token": "...",
    "refresh_token": "...",
    "expires_in": 3600
  }
}
```

---

#### `POST /auth/exchange`
Exchange authorization code for tokens (alternative to callback).

**Request:**
```json
{
  "code": "authorization_code_from_idp",
  "state": "state_from_login_response"
}
```

**Response:** TokenResponse with access_token, id_token, refresh_token

---

#### `GET /auth/userinfo`
Get current user information from access token.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "sub": "user_12345",
  "email": "john.doe@example.com",
  "name": "John Doe",
  "tenant_id": "tenant_abc",
  "roles": ["Developer"],
  "email_verified": true,
  "mfa_enabled": true
}
```

---

#### `POST /auth/validate-token`
Validate JWT token signature and claims.

**Headers:**
```
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "valid": true,
  "payload": {
    "sub": "user_12345",
    "tenant_id": "tenant_abc",
    "roles": ["Developer"],
    "exp": 1735689600
  }
}
```

---

#### `POST /auth/logout`
Logout user and revoke session.

**Request:**
```json
{
  "session_id": "session_id_to_revoke"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

### RBAC Endpoints

#### `POST /rbac/check-permission`
Check if user roles grant required permission.

**Request:**
```json
{
  "roles": ["Developer"],
  "permission": "write"
}
```

**Response:**
```json
{
  "has_permission": true,
  "roles": ["Developer"],
  "permission": "write"
}
```

---

#### `GET /rbac/roles`
Get all available roles and their permissions.

**Response:**
```json
{
  "roles": {
    "Admin": ["read", "write", "delete", "manage_users", "manage_tenants"],
    "Developer": ["read", "write", "execute"],
    "Analyst": ["read", "query"],
    "Viewer": ["read"]
  }
}
```

---

### Tenant Isolation Endpoints

#### `POST /tenant/validate-isolation`
Validate tenant isolation for cross-tenant access prevention.

**Request:**
```json
{
  "user_tenant_id": "tenant_abc",
  "resource_tenant_id": "tenant_abc"
}
```

**Response:**
```json
{
  "valid": true,
  "message": "Tenant isolation validated successfully"
}
```

**Error (403 Forbidden):**
```json
{
  "detail": "Cross-tenant access denied"
}
```

---

### Session Endpoints

#### `POST /session/create`
Create new session with security fingerprints.

**Request:**
```json
{
  "user_id": "user_12345",
  "token": "jwt_token_here"
}
```

**Response:**
```json
{
  "session_id": "random_session_id",
  "user_id": "user_12345",
  "expires_in": 3600
}
```

---

#### `POST /session/validate`
Validate session and detect potential hijacking.

**Request:**
```json
{
  "session_id": "session_id_to_validate"
}
```

**Response:**
```json
{
  "valid": true,
  "session_id": "...",
  "message": "Session validated successfully"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Session hijacking detected - IP address changed"
}
```

---

### Utility Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "l3_m2_security_access_control",
  "version": "1.0.0",
  "oauth_configured": true
}
```

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OAUTH_CLIENT_ID` | OAuth client ID from Identity Provider | Yes | - |
| `OAUTH_CLIENT_SECRET` | OAuth client secret | Yes | - |
| `OAUTH_REDIRECT_URI` | Callback URL for authorization code | Yes | `http://localhost:8000/auth/callback` |
| `OAUTH_AUTHORIZATION_ENDPOINT` | IdP authorization URL | Yes | - |
| `OAUTH_TOKEN_ENDPOINT` | IdP token exchange URL | Yes | - |
| `OAUTH_USERINFO_ENDPOINT` | OIDC userinfo URL | Yes | - |
| `OAUTH_ISSUER` | JWT issuer claim for validation | Yes | - |
| `JWT_SECRET_KEY` | Secret key for JWT signing/verification | Yes | - |
| `JWT_ALGORITHM` | JWT algorithm (RS256, HS256, ES256) | No | `RS256` |
| `JWT_AUDIENCE` | Expected audience claim | No | `api://default` |
| `JWT_EXPIRATION_MINUTES` | Token expiration time | No | `60` |
| `REDIS_HOST` | Redis server hostname | Yes | `localhost` |
| `REDIS_PORT` | Redis server port | Yes | `6379` |
| `REDIS_PASSWORD` | Redis password (if enabled) | No | - |
| `SESSION_SECRET_KEY` | Secret key for session encryption | Yes | - |
| `SESSION_TIMEOUT_SECONDS` | Session TTL in seconds | No | `3600` |
| `MAX_CONCURRENT_SESSIONS` | Max sessions per user | No | `3` |
| `DATABASE_URL` | PostgreSQL connection URL | Yes | - |
| `ENABLE_IP_VALIDATION` | Enable IP address validation | No | `true` |
| `ENABLE_USER_AGENT_VALIDATION` | Enable User-Agent validation | No | `false` |
| `REQUIRE_MFA` | Enforce MFA for all users | No | `false` |

See `.env.example` for complete configuration template.

---

## How It Works

### Complete OAuth 2.0 Flow

```
┌──────┐                                        ┌─────────────┐
│ User │                                        │  Identity   │
│      │                                        │  Provider   │
└──┬───┘                                        │  (Okta)     │
   │                                            └──────┬──────┘
   │ 1. Click "Login"                                  │
   ├──────────────────────────────────────────────────►
   │    GET /auth/login                         │
   │                                            │
   │ 2. Generate PKCE pair                      │
   │    (code_verifier, code_challenge)         │
   │                                            │
   │ 3. Redirect to IdP                         │
   ├────────────────────────────────────────────►
   │    Authorization URL + code_challenge      │
   │                                            │
   │                                     4. User authenticates
   │                                        (username + password + MFA)
   │                                            │
   │ 5. Redirect back with code                 │
   ◄────────────────────────────────────────────┤
   │    /auth/callback?code=xxx&state=yyy       │
   │                                            │
   │ 6. Exchange code for tokens                │
   ├────────────────────────────────────────────►
   │    POST /token                             │
   │    code + code_verifier + client_secret    │
   │                                            │
   │ 7. Return tokens                           │
   ◄────────────────────────────────────────────┤
   │    access_token, id_token, refresh_token   │
   │                                            │
   │ 8. Create session (store in Redis)         │
   │    Save: user_id, token, IP, User-Agent    │
   │                                            │
   │ 9. Return session_id to client             │
   │                                            │
   │ 10. Subsequent requests                    │
   ├────► Validate JWT signature                │
   │      Check RBAC permissions                │
   │      Enforce tenant isolation              │
   │      Validate session fingerprints         │
```

### JWT Token Validation Workflow

```python
def validate_request(token: str, required_permission: str, resource_tenant_id: str):
    # Step 1: Validate JWT signature (MUST be first!)
    try:
        payload = jwt_validator.validate_token(token)
    except Exception:
        return 401  # Unauthorized - invalid token

    # Step 2: Extract claims
    user_id = payload["sub"]
    user_tenant_id = payload["tenant_id"]
    user_roles = payload["roles"]

    # Step 3: Check RBAC permissions
    if not check_permission(user_roles, required_permission):
        return 403  # Forbidden - insufficient permissions

    # Step 4: Enforce tenant isolation (CRITICAL!)
    try:
        validate_tenant_isolation(user_tenant_id, resource_tenant_id)
    except ValueError:
        return 403  # Forbidden - cross-tenant access denied

    # Step 5: Validate session (optional - for extra security)
    try:
        validate_session(session_id, current_ip, current_user_agent)
    except ValueError:
        return 401  # Unauthorized - session hijacking detected

    # All checks passed - allow request
    return 200
```

---

## Common Failures & Solutions

### Failure 1: Authorization Code Replay Attack

**Symptom:** Same authorization code used multiple times to obtain tokens

**Root Cause:** Authorization codes must be single-use, but system doesn't track used codes

**Fix:**
```python
# Store used codes in Redis with short TTL
used_codes = set()

def exchange_code_for_tokens(code):
    if code in used_codes:
        raise ValueError("Authorization code already used")

    used_codes.add(code)
    # Exchange code...
    # Note: In production, use Redis: redis.setex(f"used_code:{code}", 300, "1")
```

---

### Failure 2: Mismatched redirect_uri Configuration

**Symptom:** OAuth callback fails with "redirect_uri mismatch" error

**Root Cause:** `redirect_uri` in authorization request doesn't exactly match IdP configuration (trailing slash, http vs https, localhost vs 127.0.0.1)

**Fix:**
- Ensure EXACT match: `http://localhost:8000/auth/callback` (not `http://127.0.0.1:8000/auth/callback`)
- Configure BOTH in `.env` AND in IdP application settings
- In production: use HTTPS (`https://api.example.com/auth/callback`)

---

### Failure 3: Expired Token Without Graceful Refresh

**Symptom:** User session expires suddenly, forcing re-authentication without warning

**Root Cause:** System doesn't implement token refresh flow using `refresh_token`

**Fix:**
```python
def refresh_access_token(refresh_token: str):
    """Refresh access token before expiration."""
    response = requests.post(
        token_endpoint,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    )
    return response.json()

# Call 5 minutes before token expiration
```

---

### Failure 4: Session Hijacking Through IP Validation Gaps

**Symptom:** Attacker steals session cookie and accesses system from different IP

**Root Cause:** System doesn't validate IP address consistency across requests

**Fix:**
```python
# Enable strict IP validation in .env
ENABLE_IP_VALIDATION=true

# System automatically rejects requests from different IP
def validate_session(session_id, current_ip):
    session = redis.get(f"session:{session_id}")
    if session["ip_address"] != current_ip:
        raise ValueError("Session hijacking detected - IP mismatch")
```

**Trade-off:** May cause issues for users with dynamic IPs (mobile networks). Consider:
- Relaxed mode: Log warning but allow (use `ENABLE_IP_VALIDATION=false`)
- Risk-based: Require MFA when IP changes
- IP range validation: Allow same subnet

---

### Failure 5: Concurrent Session Limits Not Enforced

**Symptom:** Single user has 50+ active sessions, enabling credential sharing

**Root Cause:** No limit on concurrent sessions per user

**Fix:**
```python
# Set in .env
MAX_CONCURRENT_SESSIONS=3

def create_session(user_id, ...):
    # Get existing sessions
    sessions = redis.keys(f"session:{user_id}:*")

    if len(sessions) >= MAX_CONCURRENT_SESSIONS:
        # Revoke oldest session
        oldest = min(sessions, key=lambda s: redis.get(s)["created_at"])
        redis.delete(oldest)

    # Create new session
    redis.setex(f"session:{user_id}:{session_id}", ttl, session_data)
```

---

### Failure 6: MFA Bypass in Emergency Scenarios

**Symptom:** System has MFA enforcement but provides "emergency bypass" that gets abused

**Root Cause:** Bypass mechanism doesn't require approval or audit logging

**Fix:**
```python
def emergency_mfa_bypass(user_id, reason, approver):
    """Emergency MFA bypass with audit trail."""
    # Require admin approval
    if not check_permission(approver.roles, "manage_users"):
        raise PermissionError("Only admins can approve MFA bypass")

    # Log to audit trail
    audit_log.critical(
        f"MFA BYPASS: user={user_id}, reason={reason}, "
        f"approver={approver.email}, timestamp={datetime.utcnow()}"
    )

    # Grant temporary bypass (24 hours max)
    redis.setex(f"mfa_bypass:{user_id}", 86400, reason)

    # Alert security team
    send_security_alert(f"MFA bypass granted for {user_id}")
```

---

### Failure 7: Tenant Isolation Bypass in Raw SQL Queries

**Symptom:** Developer writes raw SQL that doesn't filter by `tenant_id`, causing cross-tenant leak

**Root Cause:** ORM doesn't enforce tenant filtering on raw queries

**Fix:**
```python
# ❌ DANGEROUS - no tenant filtering
results = db.execute("SELECT * FROM documents WHERE id = ?", [doc_id])

# ✅ SAFE - always include tenant_id
results = db.execute(
    "SELECT * FROM documents WHERE id = ? AND tenant_id = ?",
    [doc_id, user_tenant_id]
)

# Better: Use ORM with automatic tenant scoping
class Document(Base):
    __tablename__ = "documents"

    @classmethod
    def query_for_tenant(cls, tenant_id):
        return session.query(cls).filter(cls.tenant_id == tenant_id)
```

---

### Failure 8: Token Validation Without Signature Check

**Symptom:** Attacker modifies JWT payload (changes `tenant_id` or `roles`) and gains unauthorized access

**Root Cause:** System checks claims BEFORE validating signature

**Fix:**
```python
# ❌ WRONG ORDER - checks claims first
payload = jwt.decode(token, verify=False)  # NEVER DO THIS
if payload["exp"] > time.time():
    allow_access()

# ✅ CORRECT ORDER - signature first
try:
    payload = jwt.decode(
        token,
        secret_key,
        algorithms=["RS256"],
        options={"verify_signature": True}  # ALWAYS verify signature first!
    )
except Exception:
    return 401  # Invalid signature
```

**Critical Rule:** ALWAYS verify signature BEFORE trusting any claims.

---

## When NOT to Use

### 1. Internal Tools with Single-User Access

**Scenario:** Developer building a personal dashboard for internal use only

**Why Not:** OAuth/OIDC adds unnecessary complexity and latency (redirect flow, token validation). Basic authentication or API keys sufficient.

**Alternative:** Use API keys or basic auth for single-user tools

---

### 2. Offline-First Mobile Applications

**Scenario:** Mobile app that works without internet connectivity

**Why Not:** OAuth requires network connectivity to Identity Provider for token validation and refresh

**Alternative:** Use biometric authentication (Face ID, fingerprint) with local credential storage and background sync when online

---

### 3. Systems Without Network Access to Identity Provider

**Scenario:** Air-gapped government systems in secure facilities

**Why Not:** OAuth requires outbound HTTPS to IdP - impossible in air-gapped environments

**Alternative:** Use local LDAP/Active Directory with Kerberos authentication

---

### 4. Legacy Monolithic Systems with Deep Password Dependencies

**Scenario:** 15-year-old Java monolith with password authentication embedded throughout codebase

**Why Not:** Migrating to OAuth requires refactoring authentication layer across entire codebase - high risk and cost

**Alternative:** Phase migration:
1. Add OAuth for new features
2. Support dual authentication (password + OAuth) during transition
3. Gradually migrate modules to OAuth
4. Deprecate password auth after full migration

---

### 5. Public APIs with Anonymous Access

**Scenario:** Public weather API that doesn't require user accounts

**Why Not:** OAuth is for authenticated users - adds unnecessary friction for anonymous users

**Alternative:** Use API keys for rate limiting, no authentication for read-only public data

---

## Alternative Solutions

### Alternative 1: Basic Authentication

**Description:** Send username and password in `Authorization: Basic` header (Base64-encoded) with every request

**Pros:**
- Simple to implement (no OAuth flow complexity)
- Works offline (no IdP dependency)
- Stateless (no session management)

**Cons:**
- Credentials in every request (high exposure risk)
- No SSO support
- No MFA enforcement
- Fails SOC 2 / compliance audits
- Password rotation forces client updates

**When to use:** Internal tools, development environments, CLI tools with local credential storage

---

### Alternative 2: API Keys

**Description:** Long-lived tokens generated per user/application, sent in `X-API-Key` header

**Pros:**
- Simple implementation
- No redirect flow
- Works for service-to-service auth

**Cons:**
- No user context (can't distinguish individuals)
- Long-lived tokens (revocation difficult)
- No MFA support
- No SSO integration

**When to use:** Service accounts, CI/CD pipelines, third-party integrations with scoped permissions

---

### Alternative 3: SAML 2.0

**Description:** XML-based SSO protocol (older alternative to OIDC)

**Pros:**
- Strong enterprise SSO support
- Widely adopted in large enterprises
- Supports attribute-based access control

**Cons:**
- Complex XML parsing (security risks)
- No mobile support
- Heavyweight compared to JWT
- Harder to debug than OAuth/OIDC

**When to use:** Enterprise environments with existing SAML infrastructure, no plans to support mobile apps

---

### Alternative 4: mTLS (Mutual TLS)

**Description:** Certificate-based authentication where both client and server present certificates

**Pros:**
- Very strong authentication (cryptographic certificates)
- Works at transport layer (no application code needed)
- Prevents MITM attacks

**Cons:**
- Certificate management complexity (issuance, renewal, revocation)
- User-unfriendly (certificates hard to distribute)
- No SSO support
- Difficult for web browsers

**When to use:** Service-to-service authentication in microservices, IoT devices, government/military systems

---

### Comparison Matrix

| Feature | OAuth 2.0 / OIDC | Basic Auth | API Keys | SAML 2.0 | mTLS |
|---------|------------------|------------|----------|----------|------|
| **Token Expiration** | 1 hour (configurable) | Persistent | Long-lived | Session-based | Certificate lifetime |
| **MFA Support** | ✓ Yes | ✗ No | ✗ No | ✓ Yes | ✗ No |
| **SSO Support** | ✓ Yes | ✗ No | ✗ No | ✓ Yes | ✗ No |
| **SOC 2 Compliant** | ✓ Yes | ✗ No | ✗ No | ✓ Yes | ✓ Yes |
| **Mobile-Friendly** | ✓ Yes | ⚠️ Acceptable | ✓ Yes | ✗ No | ⚠️ Difficult |
| **Implementation Complexity** | Medium | Low | Low | High | High |
| **User Context** | ✓ Yes (JWT claims) | ✓ Yes | ✗ No | ✓ Yes | ⚠️ Limited |
| **Offline Support** | ✗ No (needs IdP) | ✓ Yes | ✓ Yes | ✗ No | ✓ Yes |

---

## Decision Card

### Use OAuth 2.0 / OIDC When:

- ✅ **Multi-tenant system** serving 50+ business units with strict data isolation requirements
- ✅ **Regulated industry** (healthcare, finance, government) requiring SOC 2, HIPAA, or FedRAMP compliance
- ✅ **Enterprise SSO requirement** to integrate with corporate Identity Providers (Okta, Azure AD)
- ✅ **Audit trail needed** for compliance (who accessed what, when, from where)
- ✅ **MFA enforcement** required for privileged operations or sensitive data access
- ✅ **User-facing application** with login/logout UI flow
- ✅ **Token expiration** required for security (limit exposure window to 1 hour)
- ✅ **Permission scopes** needed to limit client capabilities (read-only vs full access)

### Don't Use When:

- ❌ **Single-user internal tools** where authentication overhead isn't justified
- ❌ **Systems without network access** to Identity Provider (air-gapped environments)
- ❌ **Service-to-service authentication** where mTLS or API keys are simpler
- ❌ **Public APIs** with anonymous access (no user accounts)
- ❌ **Legacy systems** with deep password authentication dependencies (high migration cost)
- ❌ **Offline-first mobile apps** requiring local authentication without IdP connectivity
- ❌ **Development/testing environments** where simplified auth reduces friction

### Key Trade-offs:

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Security** | Strong authentication with MFA, short-lived tokens, SSO | Implementation complexity, dependency on IdP availability |
| **User Experience** | Single Sign-On (one login for all apps) | Redirect flow adds latency (2-3 seconds) |
| **Compliance** | SOC 2 / HIPAA compliant out of box | Must configure audit logging, secure token storage |
| **Scalability** | Stateless JWT tokens (no server session state) | Redis required for session management and token revocation |
| **Maintainability** | Delegate auth to IdP (no password storage/reset logic) | Vendor lock-in to IdP, migration complexity if changing providers |
| **Multi-Tenancy** | Built-in tenant isolation through JWT claims | Must enforce `tenant_id` validation on EVERY query (developer discipline) |

---

## Testing

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest --cov=src tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html
```

### Run Specific Test Categories

```bash
# Run only OAuth tests
pytest tests/test_m2_security_access_control.py::TestOAuthClient -v

# Run only RBAC tests
pytest tests/test_m2_security_access_control.py::TestRBACEngine -v

# Run only session management tests
pytest tests/test_m2_security_access_control.py::TestSessionManager -v
```

### Test Coverage Goals

- **Unit Tests:** 80%+ coverage for all core functions (OAuth, JWT, RBAC, Session)
- **Integration Tests:** End-to-end OAuth flow, token validation with real JWTs
- **Security Tests:** Tenant isolation validation, session hijacking detection, signature verification

---

## Project Structure

```
gcc_comp_m2_v1/
├── app.py                              # FastAPI application (thin wrapper)
├── config.py                           # Configuration management
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variable template
├── .gitignore                          # Git ignore rules
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample data for demonstrations
├── example_data.txt                    # Sample text data
│
├── src/                                # Source code package
│   └── l3_m2_security_access_control/ # Core business logic
│       └── __init__.py                 # OAuthClient, JWTValidator, RBACEngine, SessionManager
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M2_Security_Access_Control.ipynb  # Interactive tutorial
│
├── tests/                              # Test suite
│   └── test_m2_security_access_control.py   # Pytest unit tests
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample configuration
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API server
    └── run_tests.ps1                   # Windows: Run test suite
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Make your changes** with clear commit messages
3. **Add tests** for new functionality (maintain 80%+ coverage)
4. **Run linters:**
   ```bash
   black src/ tests/  # Code formatting
   flake8 src/ tests/  # Linting
   mypy src/           # Type checking
   ```
5. **Submit a pull request** with description of changes

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

This software is provided "as is" without warranty. Use in production environments requires proper security review and configuration.

---

## Resources

### OAuth 2.0 / OIDC Documentation

- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749) - Official OAuth specification
- [OIDC Core Specification](https://openid.net/specs/openid-connect-core-1_0.html) - OpenID Connect standard
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics) - Security guidance
- [PKCE RFC 7636](https://datatracker.ietf.org/doc/html/rfc7636) - Proof Key for Code Exchange

### Identity Provider Documentation

- [Okta Developer Documentation](https://developer.okta.com/docs/) - Okta OAuth/OIDC integration
- [Azure AD OAuth 2.0](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow) - Microsoft identity platform
- [Auth0 Documentation](https://auth0.com/docs) - Auth0 authentication platform
- [Google Identity Platform](https://developers.google.com/identity/protocols/oauth2) - Google OAuth 2.0

### JWT and Security

- [JWT.io](https://jwt.io/) - JWT debugger and documentation
- [PyJWT Documentation](https://pyjwt.readthedocs.io/) - Python JWT library
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) - Security best practices

### Libraries and Tools

- [Authlib Documentation](https://docs.authlib.org/) - OAuth/OIDC client library
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Web framework
- [Redis Documentation](https://redis.io/docs/) - Session storage
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) - Database ORM

### Compliance and Standards

- [SOC 2 Control Requirements](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report) - Trust Services Criteria
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) - Security controls
- [GDPR Authentication Requirements](https://gdpr-info.eu/) - EU data protection regulation

---

## Support

For issues or questions:

- **GitHub Issues:** [Open an issue](https://github.com/your-repo/gcc_comp_m2_v1/issues)
- **Email:** support@techvoyagehub.com
- **Documentation:** See `/docs` folder for detailed guides

---

**Version:** 1.0.0
**Last Updated:** 2024-11-16
**Maintained By:** TechVoyageHub
**Module:** L3 M2.1 — Authentication & Identity Management
**Duration:** 40-45 minutes
**Prerequisites:** Generic CCC M1-M4, GCC Compliance M1.1-M1.4
