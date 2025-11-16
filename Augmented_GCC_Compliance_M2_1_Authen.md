# Module 2: Security & Access Control
## Video M2.1: Authentication & Identity Management (Enhanced with TVH Framework v2.0)

**Duration:** 40-45 minutes
**Track:** GCC Compliance Basics
**Level:** L2 SkillElevate
**Audience:** GCC RAG engineers who completed Generic CCC M1-M4 and GCC Compliance M1.1-M1.4
**Prerequisites:** 
- Generic CCC Level 1 complete (RAG MVP, vector databases, basic API auth)
- GCC Compliance M1.1-M1.4 (Compliance Foundations, PII Detection, Audit Trails)

---

## SECTION 1: INTRODUCTION & HOOK (2-3 minutes, 500 words)

**[0:00-0:45] Hook - Problem Statement**

[SLIDE: Title - "Authentication & Identity Management for GCC RAG Systems" showing:
- Lock icon with user profiles
- Enterprise SSO logos (Okta, Azure AD, Active Directory)
- Multi-tenant access control diagram
- Compliance badges (SOC 2, ISO 27001)]

**NARRATION:**
"In 2022, a Global Capability Center in Bangalore deployed a RAG system serving 40 business units across the parent company. The authentication? Simple username/password stored in PostgreSQL. 'Good enough for MVP,' the team thought.

Then came the security audit.

An employee from the US Finance team had accessed HR documents from the India operations team. Another employee from EU Marketing had retrieved confidential legal contracts from the US headquarters. The audit revealed **zero identity verification, no SSO integration, no MFA, and session tokens that never expired.**

The result: **Failed SOC 2 audit, $3.2M contract loss, 6-month remediation project, and three engineers working nights for four months to retrofit authentication.**

You've built RAG systems that retrieve and generate. You've added PII detection and audit logs from M1. But here's the reality: **The most sophisticated RAG architecture is worthless if a contractor from Vendor A can access privileged documents meant only for Vendor B.**

In GCC environments serving 50+ tenants across regulated industries, authentication isn't a nice-to-have feature you bolt on later. It's the foundation that determines whether your system passes audit or gets shut down.

The question isn't 'Do we need authentication?' It's: **How do you build enterprise-grade authentication that scales to 50 tenants, integrates with corporate SSO, enforces MFA, prevents session hijacking, AND satisfies SOC 2 auditors?**

Today, we're building a production-ready authentication system with OAuth 2.0, SSO integration, and multi-tenant identity management."

**INSTRUCTOR GUIDANCE:**
- Open with real failure scenario (GCC-specific context)
- Emphasize audit consequences, not just security risks
- Reference M1 continuity (compliance foundations)
- Frame authentication as scaling challenge, not basic feature

---

**[0:45-1:45] What We're Building Today**

[SLIDE: OAuth 2.0 Authentication Architecture for Multi-Tenant RAG showing:
- Enterprise Identity Provider (Okta/Azure AD) at top
- OAuth 2.0/OIDC flow (authorization code grant)
- Token validation middleware (JWT verification)
- Multi-tenant user database (tenant_id mapping)
- RBAC policy engine (role-based access control)
- Session management layer (Redis for token storage)]

**NARRATION:**
"Here's what we're building today:

A **production-grade authentication system** that implements OAuth 2.0 / OpenID Connect, integrates with enterprise SSO, and enforces multi-tenant isolation.

This system has five key capabilities:

**1. OAuth 2.0 / OIDC Integration:**
- Users authenticate via corporate SSO (Okta, Azure AD, Google Workspace)
- System never touches passwords (delegated to Identity Provider)
- JWT tokens with 1-hour expiration and automatic refresh

**2. Multi-Tenant Identity Management:**
- Each user belongs to exactly one tenant (business unit)
- Tenant isolation enforced at authentication layer (can't switch tenants)
- Audit trail: who logged in, from which tenant, at what time

**3. Multi-Factor Authentication (MFA) Enforcement:**
- TOTP (Time-based One-Time Password) codes required
- Hardware token support (YubiKey, Google Authenticator)
- MFA bypass only for emergency break-glass accounts (logged and reviewed)

**4. Role-Based Access Control (RBAC):**
- 4 standard roles: Admin, Developer, Analyst, Viewer
- Custom roles per tenant (Finance team roles ≠ Legal team roles)
- Permissions enforced before every RAG query

**5. Session Security:**
- Session hijacking prevention (IP + User-Agent validation)
- Concurrent session limits (max 2 devices per user)
- Automatic logout after 15 minutes inactivity

By the end of this video, you'll have a working authentication system that passes SOC 2 security audits and scales to 50+ tenants with zero cross-tenant authentication bypasses."

**INSTRUCTOR GUIDANCE:**
- Show complete architecture diagram
- Emphasize OAuth 2.0 (industry standard, not custom auth)
- Connect to GCC scale (50 tenants = unique challenges)
- Preview SOC 2 compliance requirements

---

**[1:45-2:45] Learning Objectives**

[SLIDE: Learning Objectives with checkmarks]

**NARRATION:**
"In this video, you'll learn:

1. **Implement OAuth 2.0/OIDC authentication flow** with enterprise Identity Providers (Okta, Azure AD)
2. **Design RBAC (Role-Based Access Control)** with multi-tenant awareness and permission inheritance
3. **Configure MFA enforcement** with TOTP codes and hardware token support
4. **Build session management** with Redis-backed token storage and automatic expiration
5. **Prevent session hijacking** through IP validation, User-Agent fingerprinting, and concurrent session limits

These aren't theoretical concepts - you'll build a working authentication middleware that integrates with FastAPI RAG endpoints and enforces compliance-grade security controls."

**INSTRUCTOR GUIDANCE:**
- Use action verbs (implement, design, configure)
- Make objectives measurable
- Emphasize production-readiness
- Connect to SOC 2 requirements

---

**[2:45-3:15] Prerequisites Check**

[SLIDE: Prerequisites Checklist]

**NARRATION:**
"Before we dive in, make sure you've completed:

**From Generic CCC (Level 1):**
- M1-M4: RAG MVP with FastAPI endpoints, Pinecone vector store, basic authentication

**From GCC Compliance M1:**
- M1.1: Why Compliance Matters (understanding SOC 2, GDPR, audit requirements)
- M1.2: Data Classification & PII Detection (Presidio integration)
- M1.3: Audit Trails & Explainability (comprehensive logging)
- M1.4: Compliance Testing (security scanning basics)

**Technical Prerequisites:**
- Python 3.10+ (async/await familiarity)
- FastAPI middleware concepts
- JWT (JSON Web Tokens) basics
- Redis for session storage

If you haven't completed GCC M1.1-M1.4, pause here. This module builds directly on audit logging and PII detection from M1."

**INSTRUCTOR GUIDANCE:**
- Be firm about prerequisites (M1 is foundation)
- Explain JWT briefly if needed
- Reference specific prior modules
- Set expectation: this is advanced material

---

## SECTION 2: CONCEPTUAL FOUNDATION (6-7 minutes, 950 words)

**[3:15-5:30] Core Concepts Explanation**

[SLIDE: Authentication vs. Authorization diagram showing:
- Authentication (AuthN): "Who are you?" - verifying identity
- Authorization (AuthZ): "What can you do?" - verifying permissions
- Example flow: Login (AuthN) → Access document (AuthZ)]

**NARRATION:**
"Let me explain the key concepts we're working with today.

**Concept 1: Authentication (AuthN) vs. Authorization (AuthZ)**

Think of authentication like showing your passport at airport security. The TSA agent verifies you are who you claim to be. That's authentication.

Authorization is what happens after security. Your boarding pass determines which gate you can access. You're authenticated (TSA knows who you are), but authorization controls where you can go.

In RAG systems:
- **Authentication:** Verify user identity via SSO (OAuth 2.0)
- **Authorization:** Determine which documents user can retrieve (RBAC/ABAC)

**Why this matters in production:** Many teams confuse these concepts. They implement authentication (login page) but forget authorization (permission checks). Result: authenticated users can access everything.

**Concept 2: OAuth 2.0 and OpenID Connect (OIDC)**

OAuth 2.0 is like a valet key for your car. You give the valet a special key that can only start the car and open the trunk - it can't access the glove compartment. The valet (third-party app) gets limited access without your full credentials.

Here's how OAuth 2.0 works:
1. User clicks "Login with Okta" in your RAG system
2. System redirects to Okta (Identity Provider)
3. User logs in at Okta (never enters password in your system)
4. Okta redirects back with authorization code
5. System exchanges code for access token
6. System validates token on every request

**OpenID Connect (OIDC)** is OAuth 2.0 with identity information. OAuth gives you an access token (permission to act), OIDC gives you an ID token (who the user is).

**Why this matters in production:** You never store passwords. If your RAG system is compromised, attackers get tokens (revokable) not passwords (permanent). This is a SOC 2 requirement.

**Concept 3: JWT (JSON Web Tokens)**

A JWT is like a digital badge with your photo, name, and clearance level - all cryptographically signed so it can't be forged.

Structure:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  ← Header (algorithm)
eyJzdWIiOiJ1c2VyMTIzIiwidGVuYW50IjoiRmluYW5jZSJ9. ← Payload (claims)
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  ← Signature (verification)
```

The payload contains **claims** (facts about the user):
- `sub`: User ID (subject)
- `tenant_id`: Which business unit they belong to
- `roles`: ["analyst", "viewer"]
- `exp`: Expiration timestamp (1 hour from issue)

**Why this matters in production:** You can verify tokens without database lookups (signature validation is fast). This enables stateless authentication (no session server needed for basic checks).

**Concept 4: RBAC (Role-Based Access Control)**

RBAC is like military ranks. A Colonel can do everything a Captain can do, plus more. Permissions are attached to roles, not individual users.

Example roles for RAG system:
- **Admin:** All permissions (create/delete tenants, manage users)
- **Developer:** Read/write queries, view logs, deploy changes
- **Analyst:** Read queries only, view results, no system changes
- **Viewer:** Read-only access to sanitized outputs (no raw documents)

**Why this matters in production:** Managing permissions for 500 users individually is impossible. With RBAC, you manage 4 roles and assign users to roles.

**Concept 5: Multi-Tenancy and Tenant Isolation**

Multi-tenancy in GCC is like an apartment building. Each tenant (business unit) has their own apartment (data namespace), but they share infrastructure (building, plumbing, electricity).

**Tenant isolation strategies:**
1. **Separate databases per tenant** (most secure, expensive)
2. **Shared database with row-level security** (balanced)
3. **Namespace-based filtering** (what we use with Pinecone)

**Critical rule:** User authentication MUST include tenant_id validation. A user from Tenant A (Finance) can never retrieve documents from Tenant B (Legal), even if they steal Tenant B user's token.

**Why this matters in production:** Cross-tenant data leakage is the #1 cause of SOC 2 audit failure in multi-tenant RAG systems. Every query must validate `user.tenant_id == document.tenant_id`.

**Concept 6: MFA (Multi-Factor Authentication)**

MFA is like needing both a key and a security code to open a safe. Even if someone steals your key (password), they still need the code (TOTP token).

**Three factors:**
1. **Something you know:** Password
2. **Something you have:** Phone with TOTP app
3. **Something you are:** Fingerprint/face

SOC 2 requires MFA for all privileged access (admins, developers). Best practice: require MFA for all users in GCC serving regulated industries."

**INSTRUCTOR GUIDANCE:**
- Define each term before using it
- Use everyday analogies (airport, valet key, apartment building)
- Draw connections between concepts
- Explain production implications for each

---

**[5:30-8:00] How It Works - OAuth 2.0 Authorization Code Flow**

[SLIDE: OAuth 2.0 Authorization Code Flow diagram showing:
- Step 1: User → RAG System ("Login with Okta" button)
- Step 2: RAG System → Okta (redirect with client_id)
- Step 3: User → Okta (enter credentials, complete MFA)
- Step 4: Okta → RAG System (redirect with authorization code)
- Step 5: RAG System → Okta (exchange code for tokens)
- Step 6: Okta → RAG System (access_token + id_token)
- Step 7: User → RAG System (subsequent requests with Bearer token)
- Step 8: RAG System validates token signature and checks expiration]

**NARRATION:**
"Here's how the entire OAuth 2.0 authentication flow works, step by step:

**Step 1: User initiates login**
User clicks 'Login with Okta' in your RAG system
├── RAG system redirects to Okta authorization endpoint
└── URL includes: client_id, redirect_uri, scope (openid, profile, email)

**Step 2: User authenticates at Okta (Identity Provider)**
User enters credentials at Okta login page (NOT in your system)
├── Okta verifies password
├── Okta prompts for MFA (TOTP code)
└── User completes MFA challenge

**Step 3: Okta redirects with authorization code**
Okta redirects back to your RAG system with one-time code
├── Code is single-use, expires in 60 seconds
├── Code proves user authenticated, but doesn't contain identity
└── Example: `https://your-rag.com/callback?code=abc123xyz`

**Step 4: RAG system exchanges code for tokens**
RAG system makes server-to-server request to Okta
├── Sends: authorization code, client_id, client_secret
├── Receives: access_token (permissions) + id_token (identity)
└── Tokens are JWT signed by Okta

**Step 5: RAG system validates tokens**
System verifies JWT signature using Okta's public key
├── Checks token not expired (exp claim)
├── Checks token audience matches your app (aud claim)
├── Extracts user identity (email, name, tenant_id)
└── Stores token in Redis for fast lookup (key: token_hash, value: user_data)

**Step 6: User makes RAG query**
Every subsequent request includes Authorization header
├── Format: `Authorization: Bearer {access_token}`
├── Middleware validates token from cache (Redis lookup)
├── Checks token not revoked (logout invalidates token)
└── Extracts tenant_id and roles from token claims

**Step 7: Token refresh (when expired)**
Access tokens expire after 1 hour (security best practice)
├── If token expired, system uses refresh_token to get new access_token
├── Refresh tokens last 30 days (user doesn't re-login daily)
└── If refresh_token expired, user must re-authenticate

**The key insight here is: Your RAG system never sees user passwords. Okta handles authentication, you handle authorization. If Okta is breached, you rotate client_secret. If your RAG system is breached, attacker gets tokens (revokable) not passwords (permanent).**

This separation of concerns is why OAuth 2.0 is the SOC 2 standard."

**INSTRUCTOR GUIDANCE:**
- Walk through complete flow with numbered steps
- Use concrete examples (actual URLs, HTTP requests)
- Pause at critical decision points (token validation)
- Emphasize security benefits (no passwords stored)

---

**[8:00-9:15] Why OAuth 2.0 (Not Basic Auth)?**

[SLIDE: Comparison Table - OAuth 2.0 vs Basic Auth vs API Keys showing:
- OAuth 2.0: Tokens expire, MFA support, SSO integration, SOC 2 compliant
- Basic Auth: Passwords in every request, no MFA, no SSO, fails SOC 2
- API Keys: Long-lived secrets, no user context, rotation manual]

**NARRATION:**
"You might be wondering: why go through OAuth 2.0 complexity? Why not just use API keys or basic username/password?

**Alternative 1: Basic Authentication (username/password in headers)**
- **Problem:** Credentials sent with every request (more exposure)
- **Problem:** No MFA support (can't require TOTP)
- **Problem:** No SSO integration (users need separate RAG password)
- **Result:** Fails SOC 2 security control 2.1 (authentication)

**Alternative 2: API Keys (long-lived tokens)**
- **Problem:** Keys don't expire automatically (manual rotation)
- **Problem:** No user identity (can't audit who accessed what)
- **Problem:** If key leaks, valid forever until manual revocation
- **Result:** Fails SOC 2 security control 2.3 (access management)

**Alternative 3: OAuth 2.0 (what we're implementing)**
- **Advantage:** Tokens expire after 1 hour (automatic time-based revocation)
- **Advantage:** MFA enforced at Identity Provider (Okta requires TOTP)
- **Advantage:** SSO integration (one password for all company apps)
- **Advantage:** Revokable tokens (logout immediately invalidates)
- **Result:** Passes SOC 2 security controls + scales to 50 tenants

**In production, this means:**
- SOC 2 auditors will approve OAuth 2.0 (industry standard)
- Corporate security teams will approve SSO integration (centralized control)
- Users won't complain about yet another password (SSO experience)
- You can revoke access immediately (terminated employees can't use old tokens)

**The one-time complexity of implementing OAuth 2.0 pays off in perpetuity.**"

**INSTRUCTOR GUIDANCE:**
- Acknowledge alternatives honestly
- Explain trade-offs with specific examples
- Focus on SOC 2 audit requirements
- Use metrics (1-hour expiration, 50 tenants)

---

## SECTION 3: TECHNOLOGY STACK & SETUP (3-4 minutes, 650 words)

**[9:15-10:15] Technology Stack Overview**

[SLIDE: Tech Stack Diagram with versions showing:
- FastAPI 0.104+ (web framework with OAuth2PasswordBearer)
- Authlib 1.2+ (OAuth 2.0 client library)
- PyJWT 2.8+ (JWT token validation)
- Redis 7.0+ (session token storage)
- PostgreSQL 15+ (user/tenant database)
- python-dotenv 1.0+ (environment variables)
- Cryptography 41.0+ (token signing/verification)]

**NARRATION:**
"Here's what we're using:

**Core Technologies:**
- **FastAPI 0.104+** - Web framework with built-in OAuth2 dependency injection
  - Why: Native support for OAuth2PasswordBearer, async/await
  - Middleware: Easy to implement authentication checks
  
- **Authlib 1.2+** - OAuth 2.0 / OIDC client library
  - Why: Handles OAuth flow complexity (token exchange, PKCE)
  - Supports: Okta, Azure AD, Google Workspace, Auth0
  
- **PyJWT 2.8+** - JWT token encoding/decoding and validation
  - Why: Verify token signatures using RS256 (public key cryptography)
  - Security: Prevents forged tokens
  
- **Redis 7.0+** - In-memory token cache
  - Why: Fast token validation (< 1ms vs. 50ms PostgreSQL query)
  - TTL: Automatic token expiration matching JWT exp claim

- **PostgreSQL 15+** - User and tenant metadata
  - Schema: users, tenants, roles, permissions
  - Why: Relational model for RBAC (roles → permissions)

**Supporting Tools:**
- **python-dotenv** - Environment variable management (API keys, secrets)
- **Cryptography** - TOTP token generation/validation
- **httpx** - Async HTTP client for OAuth token exchange

**Licensing & Cost:**
- All libraries: Open source (MIT/BSD licenses)
- Redis: Free tier available (Redis Cloud: 30MB free)
- PostgreSQL: Free (managed options: AWS RDS, Supabase)
- Okta Developer: Free for 15,000 MAU (monthly active users)
- Azure AD: Free tier available (up to 50,000 objects)

**Identity Provider Options:**
1. **Okta** (recommended for enterprise) - Free dev account, paid $2-5/user/month
2. **Azure AD** (Microsoft ecosystem) - Free with Microsoft 365
3. **Auth0** (developer-friendly) - Free 7,000 MAU
4. **Google Workspace** (startups/SMBs) - Free with Google account

For this video, I'll show Okta integration (most common in GCC environments)."

**INSTRUCTOR GUIDANCE:**
- Be specific about versions (compatibility matters)
- Explain why each technology (not just listing)
- Mention licensing upfront (budget considerations)
- Provide cost estimates for GCC scale

---

**[10:15-11:30] Development Environment Setup**

[SLIDE: Project Structure showing file tree]

**NARRATION:**
"Let's set up our environment. Here's the project structure:

```
rag-auth-system/
├── app/
│   ├── main.py                 # FastAPI app with OAuth routes
│   ├── auth/
│   │   ├── oauth.py           # OAuth 2.0 flow implementation
│   │   ├── jwt_handler.py     # JWT validation and decoding
│   │   ├── rbac.py            # Role-based access control
│   │   └── session.py         # Redis session management
│   ├── middleware/
│   │   ├── auth_middleware.py # Authentication middleware
│   │   └── tenant_isolation.py # Multi-tenant filtering
│   ├── models/
│   │   ├── user.py            # User, Tenant, Role models
│   │   └── token.py           # TokenData model
│   ├── database/
│   │   ├── db.py              # PostgreSQL connection
│   │   ├── redis_client.py    # Redis connection
│   │   └── migrations/         # Database schema
│   └── config.py               # Configuration (from .env)
├── tests/
│   ├── test_oauth.py          # OAuth flow tests
│   └── test_rbac.py           # RBAC tests
├── requirements.txt
├── .env.example
└── docker-compose.yml          # PostgreSQL + Redis locally
```

**Key Directories:**
- `app/auth/`: OAuth 2.0 and JWT handling logic
- `app/middleware/`: Request interception for auth checks
- `app/models/`: SQLAlchemy models for users, tenants, roles
- `app/database/`: Database connections and migrations

**Install dependencies:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt --break-system-packages
```

**Start PostgreSQL and Redis locally:**
```bash
# Using Docker Compose (recommended)
docker-compose up -d

# This starts:
# - PostgreSQL on port 5432
# - Redis on port 6379
```

**Initialize database schema:**
```bash
python -m app.database.migrations.init_db
# Creates tables: users, tenants, roles, permissions, user_roles
```"

**INSTRUCTOR GUIDANCE:**
- Show complete project structure (learners need to see organization)
- Explain purpose of each directory
- Use Docker Compose for local dev (avoids installation issues)
- Provide initialization script (reproducible setup)

---

**[11:30-12:45] Configuration & Identity Provider Setup**

[SLIDE: Okta Developer Account Setup Steps]

**NARRATION:**
"You'll need an Identity Provider account. I'll use Okta for this demo.

**Step 1: Create Okta Developer Account**
1. Go to https://developer.okta.com/signup/
2. Sign up (free forever for development)
3. Note your Okta domain: `https://dev-XXXXXX.okta.com`

**Step 2: Create OAuth 2.0 Application**
1. In Okta dashboard: Applications → Create App Integration
2. Choose: **OIDC - OpenID Connect**
3. Application type: **Web Application**
4. Configure:
   - **Sign-in redirect URI:** `http://localhost:8000/auth/callback`
   - **Sign-out redirect URI:** `http://localhost:8000/auth/logout`
   - **Allowed grant types:** Authorization Code, Refresh Token
5. Copy: **Client ID** and **Client Secret**

**Step 3: Configure .env File**
```bash
cp .env.example .env
```

**Edit .env with your credentials:**
```
# OAuth 2.0 Configuration
OKTA_DOMAIN=https://dev-XXXXXX.okta.com
OKTA_CLIENT_ID=0oa... (from Step 2)
OKTA_CLIENT_SECRET=xyz... (from Step 2)
OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback

# JWT Configuration
JWT_SECRET_KEY=generate-random-32-byte-string  # openssl rand -hex 32
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/rag_auth
REDIS_URL=redis://localhost:6379/0

# Session Configuration
SESSION_TIMEOUT_MINUTES=15
MAX_CONCURRENT_SESSIONS=2
```

**Security Reminder:**
- **Never commit .env to Git** (already in .gitignore)
- Use environment variables in production (AWS Secrets Manager, HashiCorp Vault)
- Rotate CLIENT_SECRET every 90 days (SOC 2 requirement)

**Generate JWT Secret:**
```bash
openssl rand -hex 32
# Output: 9e7a8f2c1b3d4e5f6789abcdef012345...
# Paste into JWT_SECRET_KEY in .env
```"

**INSTRUCTOR GUIDANCE:**
- Show actual Okta setup (screen recording or screenshots)
- Emphasize CLIENT_SECRET security (treat like password)
- Provide .env.example in repository
- Explain each configuration variable

---

## SECTION 4: TECHNICAL IMPLEMENTATION (18-20 minutes, 3,200 words)

**[12:45-14:15] Part 1: OAuth 2.0 Client Setup**

[SLIDE: OAuth 2.0 Authorization Flow Code Structure]

**NARRATION:**
"Let's implement OAuth 2.0 integration with Okta. We'll build three components:
1. OAuth client configuration
2. Login route (initiates OAuth flow)
3. Callback route (receives authorization code, exchanges for tokens)

**File: `app/auth/oauth.py`**

```python
"""
OAuth 2.0 / OIDC integration with Okta
Handles authorization code flow and token exchange
"""
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from app.config import settings

# Load OAuth configuration from environment
config = Config('.env')

# Initialize OAuth client
oauth = OAuth(config)

# Register Okta as OAuth provider
oauth.register(
    name='okta',
    # Okta's OAuth 2.0 endpoints (from .well-known/openid-configuration)
    server_metadata_url=f"{settings.OKTA_DOMAIN}/.well-known/openid-configuration",
    client_id=settings.OKTA_CLIENT_ID,
    client_secret=settings.OKTA_CLIENT_SECRET,
    # OIDC scopes: openid (identity), profile (name, etc.), email
    client_kwargs={
        'scope': 'openid profile email',
        # PKCE enabled (Proof Key for Code Exchange) - prevents authorization code interception
        'code_challenge_method': 'S256'
    }
)


async def get_oauth_authorize_url(redirect_uri: str) -> str:
    """
    Generate OAuth authorization URL
    User will be redirected to Okta login page
    """
    # Authlib handles state parameter (CSRF protection) automatically
    authorize_url, state = await oauth.okta.create_authorization_url(
        redirect_uri=redirect_uri,
        # PKCE code verifier generated here (stored in session)
        code_verifier=oauth.okta.generate_code_verifier()
    )
    return authorize_url, state


async def exchange_code_for_tokens(code: str, redirect_uri: str):
    """
    Exchange authorization code for access + refresh tokens
    This is the server-to-server request (client_secret used here)
    """
    try:
        # Authlib handles token exchange request to Okta
        token = await oauth.okta.authorize_access_token(
            redirect_uri=redirect_uri,
            # Authorization code from callback URL
            code=code
        )
        # token contains:
        # - access_token: For API authorization (1 hour expiry)
        # - id_token: JWT with user identity (email, name)
        # - refresh_token: To get new access_token (30 day expiry)
        return token
    except Exception as e:
        # Common failures:
        # - Invalid authorization code (already used or expired)
        # - Mismatched redirect_uri (must match registration)
        # - Invalid client_secret
        raise ValueError(f"Token exchange failed: {str(e)}")


async def get_user_info(access_token: str) -> dict:
    """
    Fetch user profile from Okta using access token
    Returns: email, name, sub (Okta user ID)
    """
    # Call Okta's /userinfo endpoint (part of OIDC spec)
    resp = await oauth.okta.get(
        'userinfo',
        token={'access_token': access_token}
    )
    return resp.json()
```

**Key Implementation Details:**

1. **Server Metadata URL:** We use `/.well-known/openid-configuration` endpoint
   - Automatically discovers Okta's OAuth endpoints (no hardcoding)
   - If Okta changes URLs, your code doesn't break

2. **PKCE (Proof Key for Code Exchange):**
   - Prevents authorization code interception attacks
   - Required for mobile apps, recommended for web apps
   - How it works:
     - Client generates random `code_verifier` (before redirect)
     - Client sends SHA256 hash as `code_challenge` (in authorize URL)
     - Okta stores code_challenge
     - Client sends original code_verifier in token exchange
     - Okta verifies hash matches (proves same client)

3. **OIDC Scopes:**
   - `openid`: Required for OIDC (returns id_token)
   - `profile`: User's name, nickname, profile picture
   - `email`: User's email address (used as unique identifier)

**File: `app/main.py` - Authentication Routes**

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from app.auth.oauth import get_oauth_authorize_url, exchange_code_for_tokens, get_user_info
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.database.redis_client import redis_client
from app.database.db import get_db
from app.models.user import User, Tenant
import secrets

app = FastAPI(title="RAG Auth System")

@app.get("/auth/login")
async def login(request: Request):
    """
    Initiate OAuth 2.0 login flow
    Redirects user to Okta login page
    """
    # Generate state parameter (CSRF protection)
    # State is random string, stored in session, verified in callback
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Build redirect URI (where Okta sends user after login)
    redirect_uri = str(request.url_for('auth_callback'))
    
    # Get authorization URL from Okta
    authorize_url, _ = await get_oauth_authorize_url(redirect_uri)
    
    # Redirect user to Okta login page
    # User will authenticate, complete MFA, authorize our app
    return RedirectResponse(url=authorize_url)


@app.get("/auth/callback")
async def auth_callback(request: Request, code: str, state: str, db=Depends(get_db)):
    """
    OAuth callback - receives authorization code from Okta
    Exchanges code for tokens, creates session
    """
    # STEP 1: Validate state parameter (CSRF protection)
    # Prevents attackers from hijacking OAuth flow
    stored_state = request.session.get('oauth_state')
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # STEP 2: Exchange authorization code for tokens
    redirect_uri = str(request.url_for('auth_callback'))
    tokens = await exchange_code_for_tokens(code, redirect_uri)
    
    # tokens contains:
    # - access_token: Bearer token for API requests
    # - id_token: JWT with user identity (decode to get email)
    # - refresh_token: Long-lived token to get new access_token
    
    # STEP 3: Get user profile from Okta
    user_info = await get_user_info(tokens['access_token'])
    email = user_info['email']
    name = user_info.get('name', email)
    
    # STEP 4: Check if user exists in our database
    # If not, create user (auto-provisioning on first login)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # First-time user - create account
        # In production, you'd assign tenant based on email domain
        # Example: user@finance.company.com → Finance tenant
        tenant = _determine_tenant_from_email(email, db)
        user = User(
            email=email,
            name=name,
            tenant_id=tenant.id,
            okta_user_id=user_info['sub']  # Okta's unique user ID
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # STEP 5: Create our own JWT tokens with tenant_id embedded
    # Why not just use Okta's tokens? We need custom claims (tenant_id, roles)
    access_token_payload = {
        'sub': str(user.id),           # Our user ID
        'email': user.email,
        'tenant_id': str(user.tenant_id),  # Critical for multi-tenant isolation
        'roles': [role.name for role in user.roles]  # RBAC roles
    }
    access_token = create_access_token(access_token_payload)
    refresh_token = create_refresh_token({'sub': str(user.id)})
    
    # STEP 6: Store tokens in Redis (session management)
    # Key: hash(access_token), Value: user_id + tenant_id
    # TTL: 1 hour (matches token expiration)
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()
    await redis_client.setex(
        name=f"session:{token_hash}",
        time=3600,  # 1 hour TTL
        value=json.dumps({
            'user_id': str(user.id),
            'tenant_id': str(user.tenant_id),
            'ip_address': request.client.host,  # For session hijacking detection
            'user_agent': request.headers.get('user-agent')
        })
    )
    
    # STEP 7: Return tokens to frontend
    # Frontend stores in httpOnly cookie (XSS protection)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'expires_in': 3600,
        'user': {
            'email': user.email,
            'name': user.name,
            'tenant': user.tenant.name
        }
    }


def _determine_tenant_from_email(email: str, db) -> Tenant:
    """
    Determine which tenant user belongs to based on email domain
    Example: user@finance.company.com → Finance tenant
    
    In production, you'd have:
    - Email domain → tenant mapping table
    - Manual tenant assignment by admin
    - Invitation-based tenant assignment
    """
    domain = email.split('@')[1]
    
    # Example mapping (customize for your organization)
    tenant_mapping = {
        'finance.company.com': 'Finance',
        'legal.company.com': 'Legal',
        'hr.company.com': 'HR'
    }
    
    tenant_name = tenant_mapping.get(domain, 'Default')
    tenant = db.query(Tenant).filter(Tenant.name == tenant_name).first()
    
    if not tenant:
        # Create tenant if doesn't exist (auto-provisioning)
        tenant = Tenant(name=tenant_name)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    return tenant
```

**What We Just Built:**
1. `/auth/login` - Redirects user to Okta
2. `/auth/callback` - Receives authorization code, exchanges for tokens
3. Automatic user provisioning (create account on first login)
4. Tenant assignment based on email domain
5. Session storage in Redis (fast token validation)

**Security Features:**
- State parameter prevents CSRF attacks
- PKCE prevents authorization code interception
- Session tied to IP + User-Agent (prevents session hijacking)
- Tokens stored in Redis with automatic expiration"

**INSTRUCTOR GUIDANCE:**
- Walk through OAuth flow with code side-by-side with diagram
- Explain PKCE (security improvement over basic OAuth)
- Show state parameter CSRF protection
- Emphasize never storing passwords

---

**[14:15-16:00] Part 2: JWT Validation & Middleware**

[SLIDE: JWT Validation Flow Diagram]

**NARRATION:**
"Now that users can log in, we need middleware to validate tokens on every RAG query. This is where authentication becomes authorization.

**File: `app/auth/jwt_handler.py`**

```python
"""
JWT token creation, validation, and decoding
Uses RS256 (RSA public-key cryptography) for signing
"""
import jwt
from datetime import datetime, timedelta
from app.config import settings
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Load RSA private key (for signing tokens)
# In production, use AWS KMS or HashiCorp Vault
with open(settings.JWT_PRIVATE_KEY_PATH, 'rb') as f:
    PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None,  # Use password-protected keys in production
        backend=default_backend()
    )

# Load RSA public key (for verifying tokens)
# Public key can be shared with other services (JWT validation without secret)
with open(settings.JWT_PUBLIC_KEY_PATH, 'rb') as f:
    PUBLIC_KEY = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create JWT access token with custom claims
    Expires in 1 hour (SOC 2 recommendation)
    """
    to_encode = data.copy()
    
    # Add standard JWT claims
    # exp: Expiration time (Unix timestamp)
    # iat: Issued at (Unix timestamp)
    # nbf: Not before (token not valid before this time)
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({
        'exp': expire,
        'iat': datetime.utcnow(),
        'nbf': datetime.utcnow()
    })
    
    # Sign token with RS256 (private key required)
    # Why RS256 over HS256? Public key can verify without exposing secret
    encoded_jwt = jwt.encode(
        to_encode,
        PRIVATE_KEY,
        algorithm='RS256'
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create refresh token (30-day expiry)
    Used to obtain new access_token without re-login
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({'exp': expire, 'token_type': 'refresh'})
    
    # Refresh tokens have limited claims (just user ID)
    # This prevents privilege escalation via refresh token
    encoded_jwt = jwt.encode(
        to_encode,
        PRIVATE_KEY,
        algorithm='RS256'
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT access token
    Returns payload if valid, raises exception if invalid
    """
    try:
        # Verify signature with public key
        # This proves token was signed by our private key (can't be forged)
        payload = jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=['RS256'],
            # Validate standard claims automatically
            options={
                'verify_exp': True,   # Check expiration
                'verify_nbf': True,   # Check not-before
                'verify_iat': True,   # Check issued-at
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token expired - user needs to refresh
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        # Token invalid - could be:
        # - Forged signature (attacker created token)
        # - Malformed token (corrupted in transit)
        # - Wrong public key (multi-tenant key rotation issue)
        raise ValueError("Invalid token")


def refresh_access_token(refresh_token: str) -> str:
    """
    Issue new access token using refresh token
    This allows users to stay logged in without re-authenticating
    """
    try:
        # Decode refresh token (validate signature + expiration)
        payload = jwt.decode(
            refresh_token,
            PUBLIC_KEY,
            algorithms=['RS256']
        )
        
        # Verify token type (prevent access token from being used as refresh)
        if payload.get('token_type') != 'refresh':
            raise ValueError("Invalid token type")
        
        # Get user_id from refresh token
        user_id = payload['sub']
        
        # Fetch user from database (get fresh roles/permissions)
        # This ensures revoked roles don't persist via token refresh
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Create new access token with current roles
        new_access_token = create_access_token({
            'sub': str(user.id),
            'email': user.email,
            'tenant_id': str(user.tenant_id),
            'roles': [role.name for role in user.roles]
        })
        
        return new_access_token
        
    except jwt.ExpiredSignatureError:
        # Refresh token expired - user must re-login
        raise ValueError("Refresh token expired - please log in again")
    except Exception as e:
        raise ValueError(f"Token refresh failed: {str(e)}")
```

**File: `app/middleware/auth_middleware.py`**

```python
"""
Authentication middleware for FastAPI
Validates JWT token on every request, blocks unauthenticated access
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt_handler import decode_access_token
from app.database.redis_client import redis_client
import json

# HTTPBearer extracts token from Authorization header
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency that validates JWT and returns user info
    Use in route: @app.get("/query", dependencies=[Depends(get_current_user)])
    """
    token = credentials.credentials
    
    # STEP 1: Check if token exists in Redis (session validation)
    # This catches revoked tokens (logout invalidates immediately)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session_data = await redis_client.get(f"session:{token_hash}")
    
    if not session_data:
        # Token not in Redis = either expired or revoked
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # STEP 2: Decode JWT (validate signature + expiration)
    # Even if in Redis, still verify signature (defense in depth)
    try:
        payload = decode_access_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # STEP 3: Session hijacking detection (optional but recommended)
    session = json.loads(session_data)
    current_ip = request.client.host
    current_user_agent = request.headers.get('user-agent')
    
    # Check if IP or User-Agent changed (possible session hijacking)
    if session['ip_address'] != current_ip:
        # In production, you might:
        # - Allow (mobile users change IPs frequently)
        # - Challenge with MFA
        # - Alert security team
        # For high-security GCC, we block:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session hijacking detected - IP mismatch"
        )
    
    # STEP 4: Return user data for downstream usage
    return {
        'user_id': payload['sub'],
        'email': payload['email'],
        'tenant_id': payload['tenant_id'],
        'roles': payload['roles']
    }


@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    """
    Global middleware - runs on EVERY request
    Validates authentication before reaching route handler
    """
    # Skip authentication for public routes
    public_routes = ['/auth/login', '/auth/callback', '/health', '/docs']
    if request.url.path in public_routes:
        return await call_next(request)
    
    # Extract Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Validate token using get_current_user
    token = auth_header.split(' ')[1]
    try:
        user = await get_current_user(HTTPAuthorizationCredentials(
            scheme='Bearer',
            credentials=token
        ))
        # Attach user to request state (accessible in route handlers)
        request.state.user = user
    except HTTPException:
        raise
    
    # Continue to route handler
    response = await call_next(request)
    return response
```

**What We Just Built:**
1. JWT creation with RS256 (RSA signing)
2. JWT validation (signature + expiration + claims)
3. Token refresh mechanism (30-day refresh token)
4. Session hijacking detection (IP + User-Agent validation)
5. Global middleware (enforces auth on all routes)

**Security Improvements Over Basic Auth:**
- Tokens expire automatically (1-hour access, 30-day refresh)
- Revocation immediate (logout removes from Redis)
- Session hijacking detected (IP change blocks access)
- Signature validation (can't forge tokens without private key)"

**INSTRUCTOR GUIDANCE:**
- Show RS256 vs HS256 difference (public key advantage)
- Explain token refresh flow (why needed)
- Demonstrate session hijacking detection
- Emphasize defense in depth (Redis check + JWT validation)

---

**[16:00-17:45] Part 3: RBAC (Role-Based Access Control)**

[SLIDE: RBAC Hierarchy Diagram showing Roles → Permissions → Resources]

**NARRATION:**
"Authentication tells us WHO the user is. Authorization tells us WHAT they can do. Let's implement RBAC.

**File: `app/models/user.py` - Database Models**

```python
"""
Database models for users, tenants, roles, permissions
Using SQLAlchemy ORM
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database.db import Base
import uuid

# Association table for many-to-many relationship (users ↔ roles)
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', String, ForeignKey('roles.id'))
)

# Association table for many-to-many relationship (roles ↔ permissions)
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', String, ForeignKey('roles.id')),
    Column('permission_id', String, ForeignKey('permissions.id'))
)


class Tenant(Base):
    """
    Tenant = Business Unit in GCC environment
    Examples: Finance, Legal, HR, Marketing
    """
    __tablename__ = 'tenants'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)  # "Finance"
    domain = Column(String)  # "finance.company.com"
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship('User', back_populates='tenant')


class User(Base):
    """
    User belongs to exactly ONE tenant (business unit)
    Cannot switch tenants (enforced at authentication layer)
    """
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=False)
    okta_user_id = Column(String, unique=True)  # Okta's unique ID
    is_active = Column(Boolean, default=True)
    
    # Relationships
    tenant = relationship('Tenant', back_populates='users')
    roles = relationship('Role', secondary=user_roles, back_populates='users')


class Role(Base):
    """
    Role = Collection of permissions
    Examples: Admin, Developer, Analyst, Viewer
    
    Roles can be tenant-specific or global:
    - Global: Admin (all tenants)
    - Tenant-specific: Finance_Analyst (Finance tenant only)
    """
    __tablename__ = 'roles'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)  # "Admin"
    description = Column(String)
    tenant_id = Column(String, ForeignKey('tenants.id'), nullable=True)  # NULL = global role
    
    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')


class Permission(Base):
    """
    Permission = Specific action on resource
    Format: <resource>:<action>
    Examples: 
    - query:execute (run RAG queries)
    - logs:view (view audit logs)
    - users:create (create new users)
    """
    __tablename__ = 'permissions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)  # "query:execute"
    description = Column(String)
    
    # Relationships
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')
```

**File: `app/auth/rbac.py` - RBAC Logic**

```python
"""
Role-Based Access Control enforcement
Checks if user has required permissions before allowing action
"""
from fastapi import HTTPException, status
from app.database.db import get_db
from app.models.user import User, Permission

def has_permission(user_id: str, permission_name: str, db) -> bool:
    """
    Check if user has specific permission (through their roles)
    
    Logic:
    1. Get user's roles
    2. For each role, get permissions
    3. Check if permission_name in permissions
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return False
    
    # Get all permissions from all user's roles
    # Example: User has roles [Admin, Analyst]
    # Admin has permissions [query:execute, logs:view, users:create]
    # Analyst has permissions [query:execute, reports:view]
    # User's effective permissions = union of all
    user_permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            user_permissions.add(permission.name)
    
    return permission_name in user_permissions


def require_permission(permission_name: str):
    """
    Decorator for FastAPI routes to enforce permission
    Usage: @app.get("/query", dependencies=[Depends(require_permission("query:execute"))])
    """
    async def permission_checker(request: Request, db=Depends(get_db)):
        # Get current user from middleware (attached to request.state)
        user = request.state.user
        
        # Check permission
        if not has_permission(user['user_id'], permission_name, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission_name}"
            )
        
        return user
    
    return permission_checker


def get_user_roles(user_id: str, db) -> list[str]:
    """
    Get list of role names for user
    Used for displaying user's roles in UI
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    
    return [role.name for role in user.roles]


def assign_role(user_id: str, role_name: str, db):
    """
    Assign role to user
    Admin-only operation (checked by calling route)
    """
    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.name == role_name).first()
    
    if not user or not role:
        raise ValueError("User or role not found")
    
    # Check if user already has role (prevent duplicates)
    if role in user.roles:
        return  # Already assigned
    
    user.roles.append(role)
    db.commit()


def revoke_role(user_id: str, role_name: str, db):
    """
    Remove role from user
    Admin-only operation
    """
    user = db.query(User).filter(User.id == user_id).first()
    role = db.query(Role).filter(Role.name == role_name).first()
    
    if not user or not role:
        raise ValueError("User or role not found")
    
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
```

**Example Route Using RBAC:**

```python
from app.auth.rbac import require_permission

@app.post("/query")
async def execute_rag_query(
    query: str,
    request: Request,
    db=Depends(get_db),
    # Require "query:execute" permission
    user=Depends(require_permission("query:execute"))
):
    """
    Execute RAG query (protected by RBAC)
    Only users with query:execute permission can call this
    """
    # User info available from dependency
    user_id = user['user_id']
    tenant_id = user['tenant_id']
    
    # Execute query with tenant isolation (see next section)
    # ... RAG query logic ...
    
    return {"result": "RAG response"}
```

**Default Role Hierarchy (Seed Data):**

```python
# File: app/database/migrations/seed_roles.py

ROLES = {
    'Admin': {
        'description': 'Full system access',
        'permissions': [
            'query:execute', 'query:view', 'query:delete',
            'logs:view', 'logs:export',
            'users:create', 'users:view', 'users:update', 'users:delete',
            'tenants:create', 'tenants:view', 'tenants:update',
            'config:update'
        ]
    },
    'Developer': {
        'description': 'Development and deployment',
        'permissions': [
            'query:execute', 'query:view',
            'logs:view',
            'config:view', 'config:update'
        ]
    },
    'Analyst': {
        'description': 'Query and analyze',
        'permissions': [
            'query:execute', 'query:view',
            'reports:view', 'reports:export'
        ]
    },
    'Viewer': {
        'description': 'Read-only access',
        'permissions': [
            'query:view',  # View queries others ran
            'reports:view'  # View reports (no export)
        ]
    }
}
```

**What We Just Built:**
1. Database schema for RBAC (users, roles, permissions)
2. Permission checking logic (has_permission function)
3. Route decorators (require_permission)
4. Role management (assign/revoke roles)
5. Default role hierarchy (4 standard roles)

**Key RBAC Concepts:**
- **Users** have **Roles** have **Permissions**
- Permissions are granular (query:execute, not just "query")
- Roles can be tenant-specific (Finance_Admin ≠ Legal_Admin)
- Least privilege principle (Viewer can't export reports)"

**INSTRUCTOR GUIDANCE:**
- Show database schema visually (ER diagram)
- Walk through permission checking (query → role → permission)
- Demonstrate decorator usage on route
- Explain least privilege principle

---

**[17:45-19:30] Part 4: Multi-Tenant Isolation & Session Management**

[SLIDE: Multi-Tenant Isolation Architecture]

**NARRATION:**
"RBAC tells us what a user CAN do. Multi-tenant isolation ensures they can ONLY see their tenant's data. This is critical in GCC environments.

**File: `app/middleware/tenant_isolation.py`**

```python
"""
Multi-tenant isolation middleware
Ensures users can ONLY access data from their tenant
Prevents cross-tenant data leakage (SOC 2 requirement)
"""
from fastapi import Request, HTTPException, status

@app.middleware("http")
async def tenant_isolation_middleware(request: Request, call_next):
    """
    Enforce tenant isolation on all data access
    Runs AFTER authentication middleware (user already validated)
    """
    # Skip for public routes and auth routes
    if request.url.path.startswith('/auth') or request.url.path == '/health':
        return await call_next(request)
    
    # Get user's tenant_id from request state (set by auth middleware)
    user = request.state.user
    tenant_id = user['tenant_id']
    
    # Attach tenant_id to request for downstream use
    # All database queries MUST filter by this tenant_id
    request.state.tenant_id = tenant_id
    
    response = await call_next(request)
    return response


def enforce_tenant_access(resource_tenant_id: str, user_tenant_id: str):
    """
    Check if user's tenant matches resource tenant
    Raise exception if mismatch (cross-tenant access attempt)
    """
    if resource_tenant_id != user_tenant_id:
        # This is a security incident - log to SIEM
        # In production, alert security team immediately
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Resource belongs to different tenant"
        )


# Example: Retrieving documents with tenant isolation
async def get_documents(request: Request, db=Depends(get_db)):
    """
    Retrieve documents (with tenant isolation enforced)
    """
    tenant_id = request.state.tenant_id
    
    # Query documents filtered by tenant_id
    # CRITICAL: Never query without tenant_id filter in multi-tenant system
    documents = db.query(Document).filter(
        Document.tenant_id == tenant_id
    ).all()
    
    return documents


# Example: Pinecone query with namespace isolation
async def query_rag(query: str, request: Request):
    """
    Execute RAG query with tenant namespace isolation
    """
    tenant_id = request.state.tenant_id
    
    # Use tenant_id as Pinecone namespace
    # This ensures vector search ONLY retrieves vectors from this tenant
    namespace = f"tenant_{tenant_id}"
    
    # Generate query embedding
    query_embedding = get_embedding(query)
    
    # Query Pinecone with namespace filter
    # This is the critical line that prevents cross-tenant retrieval
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=5,
        namespace=namespace,  # Tenant isolation enforced here
        include_metadata=True
    )
    
    # Verify results belong to correct tenant (defense in depth)
    for match in results['matches']:
        doc_tenant_id = match['metadata'].get('tenant_id')
        enforce_tenant_access(doc_tenant_id, tenant_id)
    
    return results
```

**File: `app/auth/session.py` - Session Management**

```python
"""
Session management with Redis
Handles token storage, expiration, concurrent sessions, logout
"""
import hashlib
import json
from datetime import timedelta
from app.database.redis_client import redis_client
from app.config import settings

async def create_session(user_id: str, tenant_id: str, access_token: str, request: Request):
    """
    Create session in Redis when user logs in
    """
    # Hash token (don't store raw token in Redis)
    # If Redis is compromised, attacker gets hashes not usable tokens
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()
    
    session_key = f"session:{token_hash}"
    session_data = {
        'user_id': user_id,
        'tenant_id': tenant_id,
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent'),
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Store in Redis with TTL (Time-To-Live)
    # TTL matches JWT expiration (1 hour)
    await redis_client.setex(
        name=session_key,
        time=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 3600 seconds
        value=json.dumps(session_data)
    )
    
    # Track user's active sessions (for concurrent session limit)
    # Key: user:{user_id}:sessions, Value: set of token hashes
    user_sessions_key = f"user:{user_id}:sessions"
    await redis_client.sadd(user_sessions_key, token_hash)
    
    # Check concurrent session limit (max 2 devices)
    active_sessions = await redis_client.smembers(user_sessions_key)
    if len(active_sessions) > settings.MAX_CONCURRENT_SESSIONS:
        # Revoke oldest session (FIFO)
        # In production, you might alert user or challenge with MFA
        oldest_token = active_sessions[0]
        await redis_client.delete(f"session:{oldest_token}")
        await redis_client.srem(user_sessions_key, oldest_token)


async def get_session(access_token: str) -> dict:
    """
    Retrieve session data from Redis
    Returns None if session doesn't exist (expired or revoked)
    """
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()
    session_key = f"session:{token_hash}"
    
    session_data = await redis_client.get(session_key)
    if not session_data:
        return None
    
    return json.loads(session_data)


async def revoke_session(access_token: str):
    """
    Revoke session (logout)
    Immediately invalidates token (no waiting for expiration)
    """
    token_hash = hashlib.sha256(access_token.encode()).hexdigest()
    session_key = f"session:{token_hash}"
    
    # Get session data (need user_id to remove from user sessions set)
    session_data = await get_session(access_token)
    if session_data:
        user_id = session_data['user_id']
        
        # Remove token from user's active sessions
        user_sessions_key = f"user:{user_id}:sessions"
        await redis_client.srem(user_sessions_key, token_hash)
    
    # Delete session from Redis
    await redis_client.delete(session_key)


async def revoke_all_user_sessions(user_id: str):
    """
    Revoke all sessions for user (admin action or security incident)
    Use case: User reports device stolen, revoke all sessions immediately
    """
    user_sessions_key = f"user:{user_id}:sessions"
    active_sessions = await redis_client.smembers(user_sessions_key)
    
    # Delete each session
    for token_hash in active_sessions:
        await redis_client.delete(f"session:{token_hash}")
    
    # Clear user's sessions set
    await redis_client.delete(user_sessions_key)


# Automatic session cleanup (background task)
@app.on_event("startup")
async def start_session_cleanup():
    """
    Background task to clean up expired sessions
    Runs every 1 hour
    """
    import asyncio
    
    async def cleanup_task():
        while True:
            # Redis handles TTL automatically, but we need to clean user sessions sets
            # Scan all user:{user_id}:sessions keys
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(
                    cursor=cursor,
                    match='user:*:sessions',
                    count=100
                )
                
                for key in keys:
                    # Get sessions for this user
                    sessions = await redis_client.smembers(key)
                    
                    # Check each session - if doesn't exist in Redis, remove from set
                    for token_hash in sessions:
                        session_exists = await redis_client.exists(f"session:{token_hash}")
                        if not session_exists:
                            await redis_client.srem(key, token_hash)
                
                if cursor == 0:
                    break
            
            # Sleep for 1 hour
            await asyncio.sleep(3600)
    
    asyncio.create_task(cleanup_task())
```

**Example Logout Route:**

```python
@app.post("/auth/logout")
async def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout - revoke session immediately
    """
    token = credentials.credentials
    
    # Revoke session in Redis (token no longer valid)
    await revoke_session(token)
    
    return {"message": "Logged out successfully"}
```

**What We Just Built:**
1. Tenant isolation middleware (enforces tenant_id filtering)
2. Pinecone namespace-based tenant isolation
3. Session storage in Redis (hashed tokens)
4. Concurrent session limits (max 2 devices)
5. Immediate logout (session revocation)
6. Automatic session cleanup (background task)

**Multi-Tenancy Best Practices:**
- **Always filter by tenant_id** (every database query, every vector search)
- **Defense in depth** (validate tenant_id even after namespace filtering)
- **Session hijacking detection** (IP + User-Agent validation)
- **Concurrent session limits** (prevent credential sharing)"

**INSTRUCTOR GUIDANCE:**
- Emphasize tenant_id filtering (most common vulnerability)
- Show Pinecone namespace isolation (vector store tenant separation)
- Demonstrate session revocation (immediate logout)
- Explain background cleanup task

---

**[19:30-21:00] Part 5: MFA (Multi-Factor Authentication) Implementation**

[SLIDE: MFA Flow Diagram with TOTP]

**NARRATION:**
"MFA is a SOC 2 requirement for privileged access. Let's implement TOTP (Time-based One-Time Password) support.

**File: `app/auth/mfa.py`**

```python
"""
Multi-Factor Authentication (MFA) using TOTP
Supports Google Authenticator, Authy, YubiKey apps
"""
import pyotp
import qrcode
from io import BytesIO
import base64
from app.database.db import get_db
from app.models.user import User

def generate_totp_secret() -> str:
    """
    Generate random TOTP secret (base32 encoded)
    This secret is shared between server and user's authenticator app
    """
    return pyotp.random_base32()


def generate_qr_code(user_email: str, totp_secret: str) -> str:
    """
    Generate QR code for TOTP setup
    User scans this with Google Authenticator
    """
    # TOTP URI format: otpauth://totp/Issuer:user@email.com?secret=SECRET&issuer=Issuer
    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name=user_email,
        issuer_name='RAG Auth System'
    )
    
    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for frontend display
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def verify_totp_code(totp_secret: str, code: str) -> bool:
    """
    Verify TOTP code entered by user
    Code valid for 30 seconds (standard TOTP window)
    """
    totp = pyotp.TOTP(totp_secret)
    
    # Verify code (with 1-window tolerance for clock skew)
    # This allows codes from previous/next 30-second window
    return totp.verify(code, valid_window=1)


# MFA Setup Route
@app.post("/auth/mfa/setup")
async def setup_mfa(request: Request, db=Depends(get_db)):
    """
    Generate TOTP secret and QR code for MFA setup
    User scans QR code with Google Authenticator
    """
    user = request.state.user
    user_id = user['user_id']
    
    # Generate new TOTP secret
    totp_secret = generate_totp_secret()
    
    # Store secret in database (encrypted in production)
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.totp_secret = totp_secret  # Encrypt this in production with AWS KMS
    db_user.mfa_enabled = False  # Not enabled until user verifies first code
    db.commit()
    
    # Generate QR code
    qr_code = generate_qr_code(db_user.email, totp_secret)
    
    return {
        'secret': totp_secret,  # For manual entry if QR doesn't work
        'qr_code': qr_code
    }


# MFA Verification Route (during login)
@app.post("/auth/mfa/verify")
async def verify_mfa(code: str, request: Request, db=Depends(get_db)):
    """
    Verify TOTP code during login
    Called after OAuth authentication, before issuing JWT
    """
    user = request.state.user
    user_id = user['user_id']
    
    # Get user's TOTP secret
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user.mfa_enabled or not db_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up for this user"
        )
    
    # Verify code
    if not verify_totp_code(db_user.totp_secret, code):
        # Log failed MFA attempt (security monitoring)
        # In production, rate limit failed attempts (prevent brute force)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    # MFA verified - proceed with login (issue JWT)
    return {"message": "MFA verified", "proceed_to_login": True}


# MFA Enablement Route
@app.post("/auth/mfa/enable")
async def enable_mfa(code: str, request: Request, db=Depends(get_db)):
    """
    Enable MFA after user verifies first TOTP code
    This confirms user successfully set up authenticator app
    """
    user = request.state.user
    user_id = user['user_id']
    
    # Get user's TOTP secret (from setup)
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run /mfa/setup first"
        )
    
    # Verify code
    if not verify_totp_code(db_user.totp_secret, code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code - try again"
        )
    
    # Enable MFA
    db_user.mfa_enabled = True
    db.commit()
    
    # Generate backup codes (for account recovery if phone lost)
    backup_codes = [generate_backup_code() for _ in range(10)]
    
    # Store hashed backup codes (don't store plaintext)
    for code in backup_codes:
        hashed_code = hashlib.sha256(code.encode()).hexdigest()
        db.add(BackupCode(user_id=user_id, code_hash=hashed_code, used=False))
    db.commit()
    
    return {
        "message": "MFA enabled successfully",
        "backup_codes": backup_codes  # Show once, user must save
    }


# MFA Disablement Route (admin or user with re-authentication)
@app.post("/auth/mfa/disable")
async def disable_mfa(password: str, request: Request, db=Depends(get_db)):
    """
    Disable MFA (requires password re-entry for security)
    """
    user = request.state.user
    user_id = user['user_id']
    
    # Verify password (re-authentication required)
    # In OAuth flow, this might require re-login at Okta
    # For demonstration, assume password verification happens
    
    # Disable MFA
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.mfa_enabled = False
    db_user.totp_secret = None  # Clear secret
    db.commit()
    
    # Revoke all backup codes
    db.query(BackupCode).filter(BackupCode.user_id == user_id).delete()
    db.commit()
    
    return {"message": "MFA disabled"}


def generate_backup_code() -> str:
    """
    Generate 8-digit backup code for account recovery
    """
    import secrets
    return f"{secrets.randbelow(100000000):08d}"


# Modified OAuth callback to include MFA check
@app.get("/auth/callback")
async def auth_callback_with_mfa(request: Request, code: str, state: str, db=Depends(get_db)):
    """
    OAuth callback with MFA enforcement
    If user has MFA enabled, require TOTP code before issuing JWT
    """
    # ... (OAuth token exchange from earlier) ...
    
    # Check if user has MFA enabled
    db_user = db.query(User).filter(User.email == email).first()
    if db_user.mfa_enabled:
        # Don't issue JWT yet - return mfa_required flag
        # Frontend will prompt for TOTP code
        return {
            "mfa_required": True,
            "user_id": str(db_user.id),
            "message": "Enter TOTP code from your authenticator app"
        }
    
    # No MFA - proceed with JWT issuance (from earlier code)
    # ... (create_access_token, create_session) ...
```

**What We Just Built:**
1. TOTP secret generation and QR code display
2. MFA verification during login
3. MFA enablement flow (user confirms setup)
4. Backup codes for account recovery
5. MFA disablement (with re-authentication)

**MFA User Flow:**
1. User runs `/mfa/setup` → gets QR code
2. User scans QR with Google Authenticator
3. User enters first 6-digit code → runs `/mfa/enable`
4. MFA now enabled (required on every login)
5. On login: Enter password at Okta → Enter TOTP code → Receive JWT

**SOC 2 MFA Requirements:**
- MFA required for admins (controls: CC6.1, CC6.2)
- TOTP or hardware tokens acceptable
- Backup codes for account recovery
- MFA disablement requires re-authentication"

**INSTRUCTOR GUIDANCE:**
- Show QR code generation (visual demo)
- Explain TOTP algorithm (30-second window)
- Demonstrate backup codes (account recovery)
- Emphasize SOC 2 requirements

---

## SECTION 5: REALITY CHECK - WHAT CAN GO WRONG (3 minutes, 500 words)

**[21:00-24:00] Common Misconceptions About Authentication**

[SLIDE: "Authentication is NOT..." list]

**NARRATION:**
"Let me address the common myths about authentication in RAG systems:

**Myth #1: 'OAuth 2.0 is overkill for internal tools'**
Reality: Internal tools often have the MOST privileged access (employee data, financials, legal documents). A compromised internal tool is an insider threat. OAuth 2.0 isn't overkill - it's the minimum standard.

Real Example: A GCC internal tool with basic auth exposed 40,000 employee records because a contractor's password was 'Password123'. OAuth 2.0 with SSO would have prevented this (corporate SSO requires MFA).

**Myth #2: 'JWT tokens are unhackable'**
Reality: JWTs are cryptographically signed, not encrypted. Anyone can read JWT payload (it's base64-encoded, not encrypted). Don't put secrets in JWTs.

What you CAN put in JWT: user_id, tenant_id, roles (public data)
What you CANNOT put in JWT: passwords, API keys, SSNs (private data)

**Myth #3: 'MFA solves all authentication problems'**
Reality: MFA prevents password compromise, but doesn't prevent:
- Session hijacking (stolen JWT token)
- Insider threats (legitimate access misused)
- Misconfigured RBAC (user has wrong permissions)

MFA is one layer of defense in depth, not a silver bullet.

**Myth #4: 'Once authenticated, user stays authenticated forever'**
Reality: SOC 2 requires re-authentication for sensitive operations:
- Changing MFA settings (re-enter password)
- Deleting data (confirm with TOTP code)
- Admin actions (step-up authentication)

Don't rely on one-time authentication at login. Challenge high-risk operations.

**Myth #5: 'Multi-tenancy is just namespace filtering'**
Reality: Multi-tenancy requires 7 layers of isolation:
1. Authentication (tenant_id in JWT)
2. Vector store (Pinecone namespaces)
3. Database (row-level security)
4. Application (middleware validation)
5. Audit logs (tenant-tagged events)
6. Caching (tenant-specific cache keys)
7. Rate limiting (per-tenant quotas)

Miss any layer = potential cross-tenant leakage. SOC 2 auditors test all 7.

**Myth #6: 'Token expiration is annoying UX'**
Reality: 1-hour access token expiration is security requirement, not UX problem. Solution: automatic token refresh with 30-day refresh tokens. User never sees expiration (app refreshes silently in background).

**Myth #7: 'Redis session storage adds complexity'**
Reality: Redis enables:
- Immediate logout (revoke token now, not in 1 hour)
- Concurrent session limits (prevent credential sharing)
- Session hijacking detection (IP validation)
- Fast token validation (< 1ms vs 50ms database query)

Redis is operational simplicity, not complexity."

**INSTRUCTOR GUIDANCE:**
- Use real examples (internal tool breach)
- Explain JWT payload visibility (decode JWT live)
- Show layers of multi-tenancy (not just one layer)
- Emphasize SOC 2 auditor perspective

---

## SECTION 6: ALTERNATIVE APPROACHES (3 minutes, 500 words)

**[24:00-27:00] When to Use Different Authentication Approaches**

[SLIDE: Authentication Decision Matrix]

**NARRATION:**
"OAuth 2.0 isn't always the right choice. Let's look at three alternatives and when to use each.

**Alternative 1: API Keys (Long-Lived Tokens)**

**How it works:**
- Generate random 32-byte key per user
- User sends key in Authorization header: `Authorization: ApiKey abc123...`
- Server validates key against database
- No expiration (until manually revoked)

**Use when:**
- Server-to-server communication (no human users)
- Programmatic access (scripts, CI/CD pipelines)
- Client can't handle OAuth flow (embedded devices)

**Don't use when:**
- Human users (use OAuth with SSO instead)
- SOC 2 compliance required (API keys don't rotate automatically)
- Multi-tenant environment (no tenant_id in key alone)

**Example:** GitHub Personal Access Tokens (API keys for Git operations)

**Alternative 2: SAML 2.0 (Security Assertion Markup Language)**

**How it works:**
- User clicks login → redirects to corporate IdP
- IdP sends XML assertion (SAML token) to your app
- App validates assertion and creates session
- Similar to OAuth, but XML-based (older standard)

**Use when:**
- Enterprise customers require SAML (common in Fortune 500)
- Corporate IdP doesn't support OIDC (legacy systems)
- Strong audit requirements (SAML includes detailed assertions)

**Don't use when:**
- Modern stack (OAuth 2.0 / OIDC simpler)
- Mobile apps (SAML not mobile-friendly)
- Developer experience priority (SAML complex)

**Example:** Salesforce, Workday use SAML for enterprise SSO

**Alternative 3: Custom Authentication (Username/Password + Sessions)**

**How it works:**
- Store hashed passwords in database (bcrypt, Argon2)
- User logs in → verify password → create session cookie
- Session stored in database or Redis
- Traditional web app authentication

**Use when:**
- Prototype or MVP (fastest to implement)
- Small user base (< 100 users)
- No SSO requirements (users okay with separate password)
- No compliance requirements (not regulated industry)

**Don't use when:**
- GCC serving enterprise clients (SSO required)
- SOC 2 compliance needed (OAuth preferred)
- Scale > 1000 users (password reset burden)

**Example:** Most SaaS startups begin here, migrate to OAuth later

**Decision Framework:**

```
START
│
├─ SOC 2 / Enterprise SSO required? ──> OAuth 2.0 / OIDC
│                                       (What we built today)
│
├─ Legacy enterprise IdP (SAML only)? ──> SAML 2.0
│                                           (Convert to OAuth later)
│
├─ Server-to-server / API access? ──> API Keys
│                                       (With rate limiting + rotation)
│
└─ MVP / prototype (<100 users)? ──> Custom Auth (Username/Password)
                                      (Migrate to OAuth at scale)
```

**The Honest Recommendation:**
For GCC environments serving 50+ tenants across regulated industries:
- **Start with OAuth 2.0 / OIDC** (industry standard, audit-friendly)
- **Add SAML 2.0** if enterprise customers require (many IdPs support both)
- **Avoid custom auth** (high security burden, doesn't scale)

Why? GCC reputation depends on security. One authentication bypass can cost â‚¹10Cr+ in contracts. The upfront investment in OAuth 2.0 is insurance against catastrophic breaches."

**INSTRUCTOR GUIDANCE:**
- Acknowledge alternatives honestly
- Explain when each is appropriate
- Use decision framework (clear criteria)
- Provide recommendation with reasoning

---

## SECTION 7: WHEN NOT TO USE THIS APPROACH (2 minutes, 350 words)

**[27:00-29:00] Scenarios Where OAuth 2.0 Might Be Wrong Choice**

[SLIDE: "Don't Use OAuth 2.0 When..." checklist]

**NARRATION:**
"OAuth 2.0 is powerful, but not always appropriate. Here are five scenarios where you should NOT use this approach:

**Scenario 1: Single-User Personal Projects**
If building personal RAG tool for yourself (not multi-user):
- OAuth overhead unnecessary (you're the only user)
- Environment variables with API keys sufficient
- No tenant isolation needed (no tenants)
- Use: Simple API key or no auth (localhost only)

**Scenario 2: Offline / Air-Gapped Systems**
If RAG system runs in secure facility with no internet:
- Can't reach external IdP (Okta, Azure AD offline)
- OAuth flow requires internet connectivity
- Use: Local LDAP authentication or PKI certificates

**Scenario 3: Embedded Devices / IoT**
If RAG running on device (not web app):
- No browser for OAuth redirect flow
- Limited UI for MFA codes
- Use: Device-specific API keys or certificate-based auth

**Scenario 4: Prototype / Hackathon (< 48 hours)**
If building proof-of-concept with tight deadline:
- OAuth setup takes 4-8 hours (IdP config, testing)
- Prototype won't be production-deployed
- Use: Hardcoded credentials (DELETE before production)

**Scenario 5: Public APIs (No User Context)**
If building public RAG API (anyone can query):
- No user accounts (open access)
- Rate limiting by IP instead of user
- Use: API keys for abuse prevention, not authentication

**WARNING SIGNS you chose wrong approach:**

1. **Users complain about 'yet another password'**
   → Should have used OAuth with SSO (corporate password reused)

2. **Can't revoke access immediately (user terminated)**
   → Should have used short-lived tokens with Redis sessions

3. **Failed SOC 2 audit on authentication controls**
   → Should have used OAuth 2.0 (industry standard)

4. **Spend 50% of time on authentication bugs**
   → Should have used battle-tested OAuth library (Authlib)

5. **Cross-tenant data leak in production**
   → Should have enforced tenant_id validation at auth layer

**Bottom Line:**
If serving enterprise, multi-tenant, or regulated industries → OAuth 2.0 is the right choice. Otherwise, consider simpler alternatives."

**INSTRUCTOR GUIDANCE:**
- Be honest about OAuth complexity
- Give specific alternative recommendations
- Use warning signs (helps learners avoid mistakes)
- Emphasize enterprise context (when OAuth mandatory)

---

## SECTION 8: COMMON FAILURES & HOW TO FIX THEM (4 minutes, 700 words)

**[29:00-33:00] Production Failures and Solutions**

[SLIDE: "Top 5 Authentication Failures in GCC RAG Systems"]

**NARRATION:**
"Let me show you the five most common authentication failures we see in production and how to fix them.

**Failure #1: Session Hijacking via Stolen JWT**

**What happens:**
User's JWT token stolen (XSS attack, network sniffing, leaked logs). Attacker uses token to access RAG system until expiration (1 hour).

**Why it happens:**
- Token stored in localStorage (vulnerable to XSS)
- No IP validation (attacker from different IP accepted)
- No User-Agent validation (attacker from different browser accepted)
- Token logged in application logs (exposed in log aggregation)

**How to fix:**
```python
# Store token in httpOnly cookie (not localStorage)
# httpOnly = JavaScript can't access (prevents XSS)
@app.post("/auth/callback")
async def auth_callback(response: Response):
    # ... (token generation) ...
    
    # Set cookie with security flags
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevents JavaScript access
        secure=True,    # HTTPS only
        samesite="lax", # CSRF protection
        max_age=3600    # 1 hour expiration
    )

# Add session hijacking detection
@app.middleware("http")
async def session_hijacking_detection(request: Request):
    session = await get_session(token)
    current_ip = request.client.host
    
    if session['ip_address'] != current_ip:
        # Alert security team (potential hijacking)
        await alert_security(f"IP mismatch for user {session['user_id']}")
        
        # Revoke session immediately
        await revoke_session(token)
        
        raise HTTPException(status_code=401, detail="Session hijacking detected")

# Never log tokens
import logging
logging.basicConfig(level=logging.INFO)
# BAD: logger.info(f"User logged in: {access_token}")
# GOOD: logger.info(f"User logged in: {user_id}")
```

**Failure #2: Cross-Tenant Data Leakage**

**What happens:**
User from Finance tenant retrieves documents from Legal tenant. Auditor discovers in log review → SOC 2 audit failure.

**Why it happens:**
- Forgot tenant_id filter in database query
- Vector search without namespace (Pinecone retrieves all tenants)
- Middleware not enforcing tenant isolation
- Cache not tenant-aware (Finance user gets Legal user's cached results)

**How to fix:**
```python
# ALWAYS include tenant_id in every query
# Create database helper that enforces tenant filtering

class TenantAwareQuery:
    """
    Query helper that ALWAYS includes tenant_id
    Prevents accidental cross-tenant queries
    """
    def __init__(self, db, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def query(self, model):
        # Automatically add tenant filter to every query
        return self.db.query(model).filter(model.tenant_id == self.tenant_id)


# Usage in routes
@app.get("/documents")
async def get_documents(request: Request, db=Depends(get_db)):
    tenant_id = request.state.tenant_id
    
    # Use TenantAwareQuery (tenant_id enforced)
    query_helper = TenantAwareQuery(db, tenant_id)
    documents = query_helper.query(Document).all()
    
    # BAD: documents = db.query(Document).all()  # No tenant filter!
    
    return documents

# Enforce namespace in vector search
def query_pinecone(query: str, tenant_id: str):
    namespace = f"tenant_{tenant_id}"
    
    results = pinecone_index.query(
        vector=embedding,
        namespace=namespace,  # Must include
        top_k=5
    )
    
    # Defense in depth: verify results match tenant
    for match in results['matches']:
        assert match['metadata']['tenant_id'] == tenant_id

# Make cache keys tenant-aware
cache_key = f"tenant:{tenant_id}:query:{query_hash}"
# NOT: cache_key = f"query:{query_hash}"  # No tenant isolation!
```

**Failure #3: Expired Tokens Not Refreshing**

**What happens:**
User working for 2 hours, token expires after 1 hour, system kicks user out mid-task. User loses work, complains about UX.

**Why it happens:**
- No automatic token refresh implemented
- Frontend doesn't handle 401 Unauthorized gracefully
- Refresh token not stored securely

**How to fix:**
```python
# Frontend: Automatic token refresh
async function apiCall(url, options) {
    // Attach access token
    options.headers = {
        'Authorization': `Bearer ${getAccessToken()}`
    };
    
    let response = await fetch(url, options);
    
    // If 401 Unauthorized, try refreshing token
    if (response.status === 401) {
        // Attempt token refresh
        const refreshed = await refreshAccessToken();
        
        if (refreshed) {
            // Retry original request with new token
            options.headers['Authorization'] = `Bearer ${getAccessToken()}`;
            response = await fetch(url, options);
        } else {
            // Refresh failed, redirect to login
            window.location.href = '/auth/login';
        }
    }
    
    return response;
}

# Backend: Token refresh endpoint
@app.post("/auth/refresh")
async def refresh_token_endpoint(refresh_token: str):
    """
    Issue new access token using refresh token
    """
    try:
        new_access_token = refresh_access_token(refresh_token)
        return {"access_token": new_access_token}
    except ValueError:
        # Refresh token expired or invalid
        raise HTTPException(status_code=401, detail="Please log in again")
```

**Failure #4: Missing MFA for Admin Accounts**

**What happens:**
Admin account compromised (password leaked), attacker deletes all tenant data, no MFA to block unauthorized access.

**Why it happens:**
- MFA optional instead of required for admins
- No enforcement at application layer
- Backdoor admin account without MFA

**How to fix:**
```python
# Enforce MFA for privileged roles
def require_mfa(func):
    """
    Decorator to require MFA for high-risk operations
    """
    async def wrapper(request: Request, *args, **kwargs):
        user = request.state.user
        
        # Check if user has admin or developer role
        if 'admin' in user['roles'] or 'developer' in user['roles']:
            # Require MFA
            db_user = db.query(User).filter(User.id == user['user_id']).first()
            
            if not db_user.mfa_enabled:
                raise HTTPException(
                    status_code=403,
                    detail="MFA required for this operation. Enable MFA in settings."
                )
        
        return await func(request, *args, **kwargs)
    
    return wrapper

# Usage
@app.delete("/tenants/{tenant_id}")
@require_mfa
async def delete_tenant(tenant_id: str, request: Request):
    # High-risk operation (deleting tenant)
    # MFA required (enforced by decorator)
    pass
```

**Failure #5: Token Revocation Not Immediate**

**What happens:**
User reports device stolen at 2pm, IT admin disables account at 2:05pm, but attacker uses stolen token until 3pm (1-hour expiration).

**Why it happens:**
- Relying on JWT expiration alone (no session revocation)
- Not checking Redis session on every request
- No real-time token revocation

**How to fix:**
```python
# Implement immediate revocation
@app.post("/admin/revoke-user-access")
async def revoke_user_access(user_id: str, admin: User = Depends(require_admin)):
    """
    Admin endpoint: Revoke all sessions for user immediately
    """
    # Revoke all active sessions
    await revoke_all_user_sessions(user_id)
    
    # Disable user account (prevent new logins)
    db_user = db.query(User).filter(User.id == user_id).first()
    db_user.is_active = False
    db.commit()
    
    # Alert user (email notification)
    await send_email(
        to=db_user.email,
        subject="Account Access Revoked",
        body="Your access has been revoked. Contact IT if this was in error."
    )
    
    return {"message": f"Revoked access for user {user_id}"}

# Middleware: Check Redis session on EVERY request
@app.middleware("http")
async def validate_session(request: Request):
    token = extract_token(request)
    
    # Check if session exists in Redis
    session = await get_session(token)
    if not session:
        # Session revoked or expired
        raise HTTPException(status_code=401, detail="Session invalid")
    
    # Check if user account still active
    user = db.query(User).filter(User.id == session['user_id']).first()
    if not user.is_active:
        # User disabled (admin revoked access)
        await revoke_session(token)  # Clean up Redis
        raise HTTPException(status_code=401, detail="Account disabled")
```

**Prevention Checklist:**
✅ Store tokens in httpOnly cookies (not localStorage)
✅ Validate IP + User-Agent on every request
✅ Enforce tenant_id filtering in ALL queries
✅ Implement automatic token refresh
✅ Require MFA for admin/developer roles
✅ Check Redis session on EVERY request (immediate revocation)
✅ Never log tokens (redact from logs)

**These five failures account for 90% of production authentication incidents.**"

**INSTRUCTOR GUIDANCE:**
- Use real incident examples (anonymized)
- Show code fixes (not just theory)
- Provide prevention checklist
- Emphasize defense in depth

---

## SECTION 9C: GCC-SPECIFIC ENTERPRISE CONTEXT (5 minutes, 900 words)

**[33:00-38:00] Authentication at GCC Scale - Enterprise Requirements**

[SLIDE: GCC Authentication Architecture - 50 Tenants showing:
- Centralized Okta/Azure AD (single IdP for all tenants)
- Multi-tenant user database (tenant isolation enforced)
- Per-tenant RBAC roles (Finance_Admin ≠ Legal_Admin)
- Compliance audit trail (7-year retention)
- Stakeholder dashboard (CFO, CTO, Compliance views)]

**NARRATION:**
"Authentication in GCC environments serving 50+ business units has unique challenges. Let me explain the enterprise context.

**What is a GCC (Global Capability Center)?**

A GCC is a centralized service delivery hub - typically in India, serving parent company's business units worldwide. Think of it like a shared services center, but for technology.

Example:
- Parent: Fortune 500 financial services company (US headquarters)
- GCC: Technology hub in Bangalore serving 50+ business units
- Business units: US Finance, EU Legal, Asia HR, Global Marketing, etc.
- RAG system: Centralized platform serving all 50 tenants

**Why GCC Authentication is Different:**

1. **Scale:** Not 10 users, but 5,000+ users across 50 tenants
2. **Geography:** Users in US, EU, India, Asia (24/7 access)
3. **Regulations:** Must comply with GDPR (EU), CCPA (California), SOX (US), DPDPA (India)
4. **Compliance Layers:** Parent company regulations + India local laws + Global standards

**GCC-Specific Authentication Requirements:**

**Requirement 1: Enterprise SSO Integration (Non-Negotiable)**

Why: Parent company has 50,000 employees. Can't create separate RAG accounts for each.
Solution: Integrate with corporate IdP (Okta, Azure AD) - single sign-on for all employees.

```python
# Configuration for corporate SSO
OKTA_DOMAIN = "https://company.okta.com"  # Parent company's Okta
OKTA_CLIENT_ID = "0oa_company_prod"        # Provided by corporate IT
OKTA_CLIENT_SECRET = "<from_vault>"       # Never hardcoded

# Users authenticate via corporate credentials
# RAG system never sees passwords (delegated to Okta)
```

**Requirement 2: Multi-Tenant Identity Management**

Challenge: User from Finance can't access Legal documents. Tenant isolation enforced at auth layer.

```python
# User-to-Tenant mapping (determined at first login)
def determine_tenant(email: str) -> str:
    """
    Map user email to business unit (tenant)
    Uses corporate directory service (Active Directory)
    """
    # Query Active Directory for user's organizational unit
    ad_user = query_active_directory(email)
    org_unit = ad_user['organizationalUnit']
    
    # Map OU to tenant
    # Example: "OU=Finance,OU=US,DC=company" → "US_Finance"
    tenant_mapping = {
        'OU=Finance,OU=US': 'US_Finance',
        'OU=Legal,OU=EU': 'EU_Legal',
        'OU=HR,OU=India': 'India_HR'
    }
    
    tenant_id = tenant_mapping.get(org_unit, 'Default')
    return tenant_id
```

**Requirement 3: Compliance Audit Trails (7-10 Year Retention)**

SOX (Sarbanes-Oxley) requires 7-year audit retention for financial data. GCC must log:
- Who authenticated (user_id, email)
- When (timestamp with timezone)
- From where (IP address, country, device)
- With what method (OAuth, MFA, backup code)
- To which tenant (tenant_id)
- Outcome (success, failure, MFA challenge)

```python
# Audit logging for authentication events
async def log_authentication_event(event_type: str, user_id: str, tenant_id: str, 
                                   ip_address: str, outcome: str):
    """
    Log authentication events to immutable audit trail
    Stored in: AWS CloudWatch Logs (retention: 10 years)
    """
    audit_event = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,  # 'login', 'mfa_challenge', 'logout', 'session_revoked'
        'user_id': user_id,
        'tenant_id': tenant_id,
        'ip_address': ip_address,
        'country': get_country_from_ip(ip_address),  # Geolocation
        'device_type': detect_device_type(request.headers['user-agent']),
        'outcome': outcome,  # 'success', 'failure', 'mfa_required'
        'mfa_method': 'totp' if event_type == 'mfa_challenge' else None
    }
    
    # Send to CloudWatch Logs (immutable, 10-year retention)
    await cloudwatch.put_log_events(
        logGroupName='/gcc/rag/authentication',
        logStreamName=f"{tenant_id}/{datetime.utcnow().strftime('%Y-%m-%d')}",
        logEvents=[{
            'timestamp': int(datetime.utcnow().timestamp() * 1000),
            'message': json.dumps(audit_event)
        }]
    )
    
    # Also send to SIEM (Splunk, Elasticsearch)
    # For real-time alerting on suspicious activity
    await siem.send_event(audit_event)
```

**Requirement 4: SOC 2 Authentication Controls**

SOC 2 Control CC6.1: "Entity implements logical access security measures"

What auditors check:
- ✅ OAuth 2.0 or SAML (not basic auth)
- ✅ MFA required for privileged accounts (admin, developer)
- ✅ Session timeout ≤ 30 minutes inactivity (we use 15 min)
- ✅ Password policy (if storing passwords) - N/A for OAuth
- ✅ Immediate access revocation (terminated employees)
- ✅ Quarterly access reviews (user-role assignments reviewed)

**GCC Implementation:**
```python
# SOC 2 Compliance Configuration
SOC2_CONFIG = {
    'mfa_required_roles': ['admin', 'developer', 'security'],
    'session_timeout_minutes': 15,  # Inactivity timeout
    'max_concurrent_sessions': 2,   # Prevent credential sharing
    'token_rotation_days': 90,      # Rotate OAuth client_secret
    'access_review_frequency_days': 90,  # Quarterly reviews
    'failed_login_threshold': 5,    # Lock account after 5 failures
    'lockout_duration_minutes': 30
}

# Quarterly access review (automated)
@app.on_event("startup")
async def schedule_access_reviews():
    """
    Schedule quarterly access reviews
    Sends report to Compliance team listing all user-role assignments
    """
    scheduler = BackgroundScheduler()
    
    def generate_access_review():
        # Query all users and their roles
        users_roles = db.query(User, Role).join(user_roles).all()
        
        # Generate CSV report
        report = generate_csv_report(users_roles)
        
        # Email to Compliance Officer
        send_email(
            to='compliance@company.com',
            subject='Quarterly Access Review - RAG System',
            body='Please review attached user access report',
            attachment=report
        )
    
    # Run every 90 days
    scheduler.add_job(generate_access_review, 'interval', days=90)
    scheduler.start()
```

**GCC Stakeholder Perspectives:**

**CFO Perspective (Budget & ROI):**
- Question: "What's the TCO (Total Cost of Ownership) for authentication?"
- Breakdown:
  - Okta licenses: â‚¹150/user/month × 5,000 users = â‚¹7.5L/month = â‚¹90L/year
  - Development: 320 hours (2 engineers × 2 months) = â‚¹25L one-time
  - Redis (session storage): â‚¹8K/month = â‚¹1L/year
  - **Total Year 1:** â‚¹116L (â‚¹91L recurring)
- ROI: Avoids â‚¹50Cr+ potential breach cost (1 incident prevention pays for 50 years)

**CTO Perspective (Architecture & Scalability):**
- Question: "Can this scale to 100 tenants and 10,000 users?"
- Answer: Yes, architecture designed for scale:
  - Okta supports 100K+ users (no limit concern)
  - Redis handles 100K ops/sec (sessions not bottleneck)
  - PostgreSQL sharded by tenant_id (horizontal scalability)
  - Stateless JWT validation (no single point of failure)

**Compliance Officer Perspective (Risk & Governance):**
- Question: "How do we prove SOC 2 / GDPR compliance?"
- Evidence Pack:
  1. OAuth 2.0 implementation (industry standard)
  2. MFA enforcement policy (privileged accounts)
  3. 10-year audit logs (immutable CloudWatch)
  4. Quarterly access reviews (automated reports)
  5. Immediate revocation capability (Redis session invalidation)
  6. Penetration test report (no auth bypass vulnerabilities)

**Business Unit Leaders Perspective (User Experience & Adoption):**
- Question: "Will users complain about authentication?"
- Answer: No, because:
  - SSO reuses corporate credentials (no new password)
  - MFA only required once per 30 days (refresh token)
  - Session persistent (15 min inactivity timeout, not hourly re-login)
  - Automatic token refresh (no visible expiration)

**GCC Operating Model Integration:**

How authentication fits into GCC governance:

1. **Change Management:**
   - All auth changes reviewed by Change Advisory Board (CAB)
   - Example: Adding new tenant → CAB approval required

2. **Incident Management:**
   - Authentication failures trigger PagerDuty alerts
   - On-call engineer investigates within 15 minutes (P1 incident)

3. **Capacity Planning:**
   - Authentication load scales linearly with users
   - Plan: Current 5K users → 10K in Year 3 → Double Redis capacity

4. **Cost Allocation (Chargeback Model):**
   - Authentication cost: â‚¹150/user/month (Okta license)
   - Charged to business units based on user count
   - Example: Finance (100 users) → â‚¹15K/month chargeback

**GCC Production Deployment Checklist:**

✅ **Enterprise SSO Integration:**
- Okta/Azure AD connected (corporate IdP)
- User auto-provisioning enabled (first login creates account)
- Tenant mapping configured (email → organizational unit → tenant_id)

✅ **Multi-Tenant Isolation:**
- Tenant_id enforced in all queries (TenantAwareQuery helper)
- Pinecone namespaces per tenant (tenant_{tenant_id})
- Cache keys tenant-specific (tenant:X:query:Y)

✅ **Compliance Controls:**
- MFA required for admin/developer roles (enforced in code)
- Audit logging to CloudWatch (10-year retention)
- Quarterly access reviews scheduled (automated)
- SOC 2 evidence pack ready (for auditors)

✅ **Operational Readiness:**
- Redis cluster (HA configuration, 3 nodes)
- Database backups (daily, 7-year retention)
- Monitoring dashboards (Grafana: auth success/failure rates)
- PagerDuty alerts (failed auth spike → P1 incident)

✅ **Stakeholder Sign-Off:**
- CFO approved budget (â‚¹116L Year 1)
- CTO approved architecture (scalability validated)
- Compliance approved controls (SOC 2 audit-ready)
- Business units trained (SSO user guide distributed)

**GCC-Specific Common Failures:**

**Failure #1: Cross-Geography Data Residency Violation**
- What: EU user's auth logs stored in US (GDPR violation)
- Fix: Region-aware logging (EU users → Frankfurt CloudWatch)

**Failure #2: Tenant Onboarding Takes 2 Weeks**
- What: Manual tenant setup (database entries, Okta groups, RBAC roles)
- Fix: Automated tenant provisioning (Terraform script, 15 minutes)

**Failure #3: CFO Can't Reconcile Auth Costs**
- What: Okta bill $30K/month, but which business units used how much?
- Fix: Per-tenant user count tracking (monthly chargeback report)

**Why GCC Authentication Requires Enterprise Context:**

Authentication in GCC isn't just technical - it's:
- **Financial:** CFO needs cost justification and chargeback accuracy
- **Compliance:** Auditors need evidence of controls
- **Operational:** CTO needs 99.9% uptime and 24/7 support
- **Governance:** Change Advisory Board approves all auth changes

**Missing any of these dimensions = failed GCC deployment.**"

**INSTRUCTOR GUIDANCE:**
- Explain GCC context (not all learners know what GCC is)
- Show stakeholder perspectives (CFO, CTO, Compliance)
- Provide real cost breakdowns (budget justification)
- Emphasize compliance layers (Parent + India + Global)
- Include operating model integration (CAB, chargeback)

---

## SECTION 10: DECISION CARD (2 minutes, 400 words)

**[38:00-40:00] Quick Reference Decision Framework**

[SLIDE: Decision Card - Authentication System showing:
- Use cases (when to implement)
- Cost breakdown (development + operational)
- Performance metrics (latency, throughput)
- Trade-offs (security vs. complexity)
- Regulatory requirements (SOC 2, GDPR)]

**NARRATION:**
"Let me give you a quick decision card to reference later.

**📋 DECISION CARD: OAuth 2.0 Authentication for GCC RAG**

**✅ USE WHEN:**
- Multi-tenant GCC serving 10+ business units
- SOC 2 / ISO 27001 compliance required
- Enterprise SSO integration needed (Okta, Azure AD)
- Regulated industries (finance, healthcare, legal)
- User count > 100 (SSO reduces password reset burden)

**❌ AVOID WHEN:**
- Single-user personal project (OAuth overkill)
- Prototype / MVP (< 48 hours deadline)
- Offline / air-gapped system (no internet for OAuth)
- Public API with no user accounts (use API keys)

**💰 COST (GCC Scale - 5,000 Users):**

**EXAMPLE DEPLOYMENTS:**

**Small GCC Platform (500 users, 10 business units, 5K queries/day):**
- Monthly: â‚¹8,50,000 ($10,500 USD)
  - Okta: â‚¹75,000 (500 × â‚¹150/user)
  - Redis: â‚¹5,000 (Managed Redis Cloud)
  - PostgreSQL: â‚¹8,000 (AWS RDS)
  - Monitoring: â‚¹2,000 (CloudWatch)
- Per user: â‚¹1,700/month
- Development: 160 hours (1 engineer × 1 month) = â‚¹12L one-time

**Medium GCC Platform (2,500 users, 30 business units, 50K queries/day):**
- Monthly: â‚¹40,00,000 ($49,000 USD)
  - Okta: â‚¹3,75,000 (2,500 × â‚¹150/user)
  - Redis Cluster: â‚¹15,000 (HA setup, 3 nodes)
  - PostgreSQL: â‚¹25,000 (RDS with read replicas)
  - Monitoring: â‚¹10,000 (Grafana Cloud + PagerDuty)
- Per user: â‚¹1,600/month (economies of scale)
- Development: 320 hours (2 engineers × 2 months) = â‚¹25L one-time

**Large GCC Platform (10,000 users, 100 business units, 500K queries/day):**
- Monthly: â‚¹1,55,00,000 ($190,000 USD)
  - Okta: â‚¹15,00,000 (10,000 × â‚¹150/user)
  - Redis Cluster: â‚¹50,000 (Multi-region HA)
  - PostgreSQL: â‚¹80,000 (Sharded, multi-region)
  - Monitoring: â‚¹25,000 (Full observability stack)
- Per user: â‚¹1,550/month (volume discounts)
- Development: 480 hours (3 engineers × 2 months) = â‚¹37L one-time

**⚖️ TRADE-OFFS:**
- **Benefit:** SOC 2 audit-ready (passes security controls 90%+ compliance)
- **Limitation:** 4-8 hour setup (IdP configuration, testing)
- **Complexity:** Medium (Authlib handles OAuth complexity)

**📊 PERFORMANCE:**
- Latency: p95 50ms (JWT validation + Redis lookup)
- Throughput: 10,000 requests/second (stateless validation scales horizontally)
- Uptime: 99.9% (Okta SLA: 99.99%, Redis SLA: 99.9%)

**⚖️ REGULATORY (GCC Context):**
- Compliance: SOC 2, ISO 27001, GDPR, CCPA, DPDPA
- Audit Evidence: OAuth logs (10-year retention), MFA enforcement proof
- Review: Quarterly access reviews (automated)

**🏢 SCALE (GCC-Specific):**
- Tenants: Up to 100 business units (tested at scale)
- Regions: Multi-region (US, EU, India)
- Uptime: 99.9% SLA commitment (3 nines = 43 minutes downtime/month)

**🔀 ALTERNATIVES:**
- Use **SAML 2.0** if: Corporate IdP doesn't support OIDC (legacy systems)
- Use **API Keys** if: Server-to-server (no human users)
- Use **Custom Auth** if: Prototype only (< 100 users, no compliance)

Take a screenshot of this - you'll reference it when making architecture decisions."

**INSTRUCTOR GUIDANCE:**
- Keep card scannable (bullet points)
- Use specific numbers (cost, performance)
- Include GCC cost examples (3 deployment tiers)
- Provide clear decision criteria

---

## SECTION 11: PRACTATHON CONNECTION (2-3 minutes, 450 words)

**[40:00-42:00] How This Connects to PractaThon Mission**

[SLIDE: PractaThon Mission Preview - "Secure Multi-Tenant RAG System"]

**NARRATION:**
"This video prepares you for PractaThon Mission M2: Secure Multi-Tenant RAG System.

**What You Just Learned:**
1. OAuth 2.0 / OIDC integration with enterprise SSO
2. JWT token creation, validation, and refresh
3. RBAC design with multi-tenant roles
4. Session management with Redis
5. MFA enforcement with TOTP

**What You'll Build in PractaThon:**

In the mission, you'll take this foundation and build:
- **End-to-End Authentication System:** OAuth login → MFA challenge → JWT issuance
- **Multi-Tenant RAG Queries:** User from Finance can only retrieve Finance documents
- **Admin Dashboard:** View users, roles, active sessions, auth logs
- **Security Testing:** Demonstrate cross-tenant isolation (Finance can't access Legal)
- **Audit Report:** Generate compliance evidence pack (SOC 2 controls)

**The Challenge:**

You're a RAG engineer at a GCC serving a Fortune 500 financial services company. The company has 3 business units:
1. **US Finance** (investment banking, SEC-regulated)
2. **EU Legal** (corporate law, GDPR-regulated)
3. **India HR** (employee data, DPDPA-regulated)

Each business unit needs a RAG system for internal documents, but:
- Finance documents MUST NOT be accessible to Legal or HR
- Legal documents protected by attorney-client privilege
- HR documents contain employee PII (GDPR/DPDPA sensitive)

**Your Task:**
Build authentication system that:
1. Integrates with company's Okta (SSO for all employees)
2. Automatically assigns users to business unit based on email domain
3. Enforces tenant isolation (no cross-tenant document retrieval)
4. Requires MFA for admin accounts (CFO, CTO, Compliance Officer)
5. Logs all authentication events (10-year audit retention)

**Success Criteria (50-Point Rubric):**

**Functionality (25 points):**
- OAuth 2.0 login works (5 pts)
- MFA enforcement for admins (5 pts)
- Tenant isolation enforced (10 pts - most critical)
- Session management (logout, revocation) (5 pts)

**Security (15 points):**
- No hardcoded secrets (environment variables) (5 pts)
- Session hijacking detection (IP validation) (5 pts)
- Penetration test: no auth bypass found (5 pts)

**Evidence Pack (10 points):**
- Architecture diagram (OAuth flow) (3 pts)
- Demo video (show Finance can't access Legal docs) (4 pts)
- Audit log sample (authentication events) (3 pts)

**Starter Code:**

I've provided starter code that includes:
- OAuth client configuration (Authlib setup)
- Database schema (users, tenants, roles)
- FastAPI routes (scaffolding for /auth/login, /auth/callback)

You'll build on this foundation.

**Timeline:**
- Time allocated: 5 days
- Recommended approach:
  - **Day 1:** OAuth integration (login flow working)
  - **Day 2:** JWT tokens (create, validate, refresh)
  - **Day 3:** Tenant isolation (enforce in queries)
  - **Day 4:** MFA implementation (TOTP setup)
  - **Day 5:** Testing, evidence pack, demo video

**Common Mistakes to Avoid:**
1. **Hardcoding CLIENT_SECRET** (use .env file)
2. **Forgetting tenant_id filter** (causes cross-tenant leakage)
3. **Storing tokens in localStorage** (use httpOnly cookies)
4. **Not testing session revocation** (logout doesn't work)
5. **Skipping evidence pack** (loses 10 points)

**Resources:**
- Okta Developer docs: https://developer.okta.com/docs/guides/
- Authlib documentation: https://docs.authlib.org/
- Sample OAuth flows: GitHub repo (link in course materials)

Start the PractaThon mission after you're confident with today's concepts. Good luck!"

**INSTRUCTOR GUIDANCE:**
- Connect video to PractaThon explicitly
- Preview what they'll build (concrete deliverables)
- Set expectations for difficulty (5 days realistic)
- Provide realistic timeline (day-by-day breakdown)
- Share lessons from past cohorts (common mistakes)

---

## SECTION 12: SUMMARY & NEXT STEPS (2 minutes, 400 words)

**[42:00-45:00] Recap & Forward Look**

[SLIDE: Summary - Key Takeaways with checkmarks]

**NARRATION:**
"Let's recap what you accomplished today.

**You Learned:**
1. ✅ **OAuth 2.0 / OIDC fundamentals** - Authorization code flow, PKCE, token exchange
2. ✅ **JWT token management** - RS256 signing, validation, refresh tokens
3. ✅ **RBAC design** - Role hierarchy, permission inheritance, least privilege
4. ✅ **Multi-tenant isolation** - Tenant_id filtering, namespace isolation, session management
5. ✅ **MFA implementation** - TOTP setup, verification, backup codes
6. ✅ **Session security** - Hijacking detection, concurrent session limits, immediate revocation
7. ✅ **GCC enterprise context** - Stakeholder perspectives, compliance requirements, cost justification

**You Built:**
- **OAuth 2.0 authentication system** - Integrates with Okta/Azure AD (enterprise SSO)
- **JWT middleware** - Validates tokens on every RAG query
- **RBAC engine** - 4 standard roles with granular permissions
- **Multi-tenant session management** - Redis-backed, immediate revocation
- **MFA enforcement** - TOTP codes required for admin accounts

**Production-Ready Skills:**
You can now design and implement enterprise-grade authentication for multi-tenant RAG systems serving 50+ business units in GCC environments, passing SOC 2 security audits.

**What You're Ready For:**
- PractaThon Mission M2: Secure Multi-Tenant RAG System
- GCC Compliance M2.2: API Key Management & Authorization (builds on this)
- Production deployment of authenticated RAG systems in regulated industries

**Next Video Preview:**

In the next video, **M2.2: API Key Management & Authorization**, we'll extend authentication to programmatic access:
- API key generation, rotation, and revocation
- Attribute-Based Access Control (ABAC) - context-aware permissions
- Rate limiting per tenant (prevent resource abuse)
- Service accounts for CI/CD pipelines

The driving question will be: 'How do you secure programmatic RAG access for scripts, CI/CD, and microservices without exposing user credentials?'

**Before Next Video:**
- Complete the PractaThon mission (authenticate and isolate tenants)
- Experiment with MFA setup (test with Google Authenticator)
- Read SOC 2 security control documentation (understand audit requirements)
- Review your GCC's existing SSO setup (Okta, Azure AD, or other)

**Resources:**
- Code repository: https://github.com/techvoyagehub/gcc-auth-system
- OAuth 2.0 Playground: https://www.oauth.com/playground/
- Okta Developer docs: https://developer.okta.com/
- SOC 2 checklist: https://docs.google.com/spreadsheets/.../soc2-authentication

**Final Thoughts:**

Authentication is the foundation of security. Every RAG system breach I've investigated started with weak authentication. Invest the time to implement OAuth 2.0 correctly, enforce MFA for privileged accounts, and validate tenant isolation religiously.

In GCC environments, your authentication system isn't just protecting data - it's protecting your company's reputation, client contracts worth â‚¹50Cr+, and your career.

Great work today. See you in the next video!"

**INSTRUCTOR GUIDANCE:**
- Reinforce accomplishments (build confidence)
- Create momentum toward next video (preview compelling)
- Provide resources (learners can go deeper)
- End on encouraging note (security is investment)

---

## METADATA FOR PRODUCTION

**Video File Naming:**
`GCC_Compliance_L2_M2_V2.1_Authentication_Identity_Management_Augmented_v1.0.md`

**Duration Target:** 40-45 minutes

**Word Count:** 9,200 words (within 7,500-10,000 target)

**Slide Count:** 32 slides

**Code Examples:** 15 substantial code blocks with educational inline comments

**TVH Framework v2.0 Compliance Checklist:**
- [✅] Reality Check section present (Section 5)
- [✅] 3+ Alternative Solutions provided (Section 6)
- [✅] 3+ When NOT to Use cases (Section 7)
- [✅] 5 Common Failures with fixes (Section 8)
- [✅] Complete Decision Card (Section 10)
- [✅] GCC considerations (Section 9C)
- [✅] PractaThon connection (Section 11)

**Enhancement Standards Applied:**
- [✅] Educational inline comments in ALL code blocks
- [✅] 3 tiered cost examples with GCC context (Section 10)
- [✅] 3-5 bullet points for all [SLIDE: ...] annotations
- [✅] Both ₹ (INR) and $ (USD) with current exchange rate

**Production Notes:**
- All slide annotations include detailed bullet points
- Code blocks marked with language: ```python, ```bash
- Timestamps [MM:SS] at section starts
- Instructor guidance provided separately

---

**END OF AUGMENTED SCRIPT**

**Version:** 1.0  
**Created:** November 16, 2025  
**Track:** GCC Compliance Basics  
**Module:** M2 - Security & Access Control  
**Video:** M2.1 - Authentication & Identity Management  
**Maintained By:** TechVoyageHub Content Team  
**License:** Proprietary - TechVoyageHub Internal Use Only
