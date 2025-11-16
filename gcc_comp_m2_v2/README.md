# L3 M2.2: Authorization & Multi-Tenant Access Control

**Track:** GCC Compliance Basics
**Module:** M2 - Security & Access Control
**Video:** M2.2 - Authorization & Multi-Tenant Access Control
**Level:** L3 (Production-Ready)
**Duration:** 40-45 minutes

## Overview

This implementation demonstrates **production-grade multi-tenant authorization** for RAG systems serving Government Community Cloud (GCC) environments with 50+ business units. The system ensures **zero cross-tenant data leakage** while maintaining performance at scale through:

- **RBAC (Role-Based Access Control):** Three-role hierarchy with granular permissions
- **ABAC (Attribute-Based Access Control):** Context-aware policies using Open Policy Agent
- **Namespace Isolation:** Database-level multi-tenant separation in Pinecone
- **Immutable Audit Logging:** 7-year retention for regulatory compliance

This module builds on M2.1 (Authentication & Identity Management) and addresses the critical question: **"Now that we know WHO the user is, what can they ACCESS?"**

## What You'll Learn

By completing this module, you will be able to:

1. **Design and implement RBAC** with three roles (Admin, Analyst, Compliance Officer) for RAG operations
2. **Build namespace-based multi-tenant isolation** in Pinecone vector database
3. **Configure ABAC using Open Policy Agent (OPA)** for context-aware access control
4. **Prove zero cross-tenant data leakage** through penetration testing and namespace enforcement
5. **Implement immutable audit logging** with 7-year retention for compliance
6. **Understand the difference** between authentication (who are you) and authorization (what can you access)
7. **Deploy policy-as-code** using Rego language for version-controlled authorization rules

## Key Concepts Covered

### 1. Authentication vs. Authorization
- **Authentication (M2.1):** Verifies identity ("Who are you?") - like a building badge
- **Authorization (M2.2):** Grants permissions ("What can you access?") - like badge access levels
- Clear separation of concerns between identity and permissions

### 2. RBAC (Role-Based Access Control)
Three-role hierarchy designed for GCC compliance:

- **Admin:** Full control over all namespaces, user management, and policy configuration
- **Analyst:** Query access ONLY to assigned namespace (e.g., Finance analyst → finance-prod)
- **Compliance Officer:** Read-only access across ALL namespaces + audit log export

**Permission Mapping:**
```
Admin:
  ✓ create_namespace, delete_namespace
  ✓ assign_user_to_namespace, manage_users
  ✓ query_own_namespace, query_all_namespaces
  ✓ manage_policies, view_audit_logs, export_audit_logs

Analyst:
  ✓ query_own_namespace

Compliance Officer:
  ✓ query_all_namespaces (read-only)
  ✓ view_audit_logs, export_audit_logs
```

### 3. ABAC (Attribute-Based Access Control)
Context-aware policies that evaluate:
- **User attributes:** Role, location, department
- **Resource attributes:** Namespace, classification (confidential/internal)
- **Environmental context:** Time of day, IP address, device type

Uses **Open Policy Agent (OPA)** for policy decisions in Rego language.

### 4. Multi-Tenant Namespace Isolation
Each business unit receives a dedicated Pinecone namespace:
- `finance-prod` → Finance department (1500 documents)
- `hr-prod` → Human Resources (800 documents)
- `legal-prod` → Legal department (600 documents)
- `admin-prod` → Administration (300 documents)

**Isolation Guarantee:** Queries to `finance-prod` can NEVER retrieve documents from `hr-prod`, enforced at the database level.

### 5. Immutable Audit Logging
Write-once audit trail for compliance:
- **Immutability:** PostgreSQL table with INSERT-only permissions (no UPDATE/DELETE)
- **Retention:** 7 years (2,555 days) for regulatory requirements (SOX, GDPR, DPDPA)
- **Fields logged:** Timestamp, user_id, action, namespace, resources_accessed, decision, policy_used

### 6. Policy-as-Code
Authorization rules stored in version control:
- **Auditability:** All policy changes tracked in Git
- **Testability:** Policies validated before deployment
- **Traceability:** Every decision linked to a specific policy version

## How It Works

### Authorization Flow (7 Steps)

```
1. User submits authenticated request
   ↓ (JWT token from M2.1 contains: user_id, role, namespace)

2. Middleware extracts user identity and claims
   ↓

3. RBAC check: Does user role have required permission?
   ↓ (Check Role-Permission Mapping)

4. ABAC evaluation: Does context satisfy policies?
   ↓ (OPA evaluates location, time, classification)

5. Namespace resolution: Which namespace is authorized?
   ↓ (Analysts → user_namespace, Admin → target_namespace)

6. Pinecone query with namespace filter
   ↓ (Database-level isolation enforced)

7. Immutable audit log entry + return response
   ✓ (Log: user_id, action, namespace, decision, timestamp)
```

### Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request (JWT Token)                 │
└───────────────────────┬─────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│           JWT Authentication (M2.1 Prerequisite)          │
│  Extract: user_id, role, namespace from token claims      │
└───────────────────────┬───────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│                   RBAC Middleware                         │
│  Roles: Admin | Analyst | Compliance Officer             │
│  Check: Role-Permission Mapping                           │
└───────────────────────┬───────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│         ABAC Policy Engine (Open Policy Agent)            │
│  Context: Location, Time, IP, Device, Classification      │
│  Rego Policy: /v1/data/gcc/authz/allow                    │
└───────────────────────┬───────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│              Namespace Isolation Layer                    │
│  Pinecone Vector DB: Row-level security via namespaces    │
│  finance-prod | hr-prod | legal-prod | admin-prod        │
└───────────────────────┬───────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────────┐
│                   Audit Logger                            │
│  PostgreSQL: Immutable audit_logs table (7-year retention)│
│  Correlation IDs from M2.3 (Encryption & Secrets)         │
└───────────────────────┬───────────────────────────────────┘
                        ↓
                 Return Response
            (Results or 403 Forbidden)
```

### Database Schema

**users table:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL,  -- admin, analyst, compliance_officer
    namespace VARCHAR(100) NOT NULL,
    location VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**namespaces table:**
```sql
CREATE TABLE namespaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    business_unit VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**audit_logs table (IMMUTABLE):**
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    namespace VARCHAR(100) NOT NULL,
    resources_accessed JSONB,
    decision VARCHAR(50) NOT NULL,  -- allowed, denied, error
    policy_used VARCHAR(100) NOT NULL,  -- RBAC, ABAC, RBAC+ABAC
    context JSONB
);

-- Grant INSERT only (no UPDATE/DELETE for immutability)
GRANT INSERT ON audit_logs TO app_user;
REVOKE UPDATE, DELETE ON audit_logs FROM app_user;
```

## Prerequisites

### Required Knowledge
- ✅ Completed Generic CCC M1-M4 (RAG MVP implementation)
- ✅ Completed GCC Compliance M2.1 (Authentication & Identity Management)
- ✅ Understanding of OAuth 2.0/OIDC and JWT tokens
- ✅ Basic knowledge of multi-tenant architectures

### Required Accounts
- Pinecone account (free tier sufficient for testing)
- Docker installation (for running OPA locally)

## Technology Stack

**Detected Services:**
- **Primary Vector Database:** Pinecone
- **User Database:** PostgreSQL 15
- **Authorization Engine:** Open Policy Agent (OPA) 0.58+
- **Authentication:** JWT/OAuth 2.0 (from M2.1)

**Core Technologies:**
- **Web Framework:** FastAPI 0.104+ (Python 3.11)
- **Database ORM:** SQLAlchemy 2.0
- **JWT Library:** PyJWT 2.8 / python-jose 3.3
- **Testing:** pytest 7.4
- **Development:** Jupyter 1.0, uvicorn 0.24

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd gcc_comp_m2_v2
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required Environment Variables:**

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `PINECONE_ENABLED` | Enable Pinecone vector DB | Yes | `true` |
| `PINECONE_API_KEY` | Your Pinecone API key | Yes | `your_key_here` |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Yes | `us-west1-gcp` |
| `PINECONE_INDEX_NAME` | Index name for GCC data | Yes | `gcc-compliance-m2` |
| `POSTGRES_ENABLED` | Enable PostgreSQL database | Yes | `true` |
| `POSTGRES_HOST` | PostgreSQL host | Yes | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | Yes | `5432` |
| `POSTGRES_DB` | Database name | Yes | `gcc_auth` |
| `POSTGRES_USER` | Database user | Yes | `postgres` |
| `POSTGRES_PASSWORD` | Database password | Yes | `your_password` |
| `OPA_ENABLED` | Enable Open Policy Agent | No | `false` |
| `OPA_URL` | OPA endpoint | No | `http://localhost:8181` |
| `JWT_SECRET_KEY` | JWT secret from M2.1 | Yes | `your_jwt_secret` |
| `JWT_ALGORITHM` | JWT algorithm | Yes | `HS256` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

### 5. Setup PostgreSQL (Optional for Full Functionality)
```bash
# Create database
createdb gcc_auth

# Run migrations (in production)
# python scripts/init_db.py
```

### 6. Setup Open Policy Agent (Optional for ABAC)
```bash
# Run OPA in Docker
docker run -d --name opa -p 8181:8181 openpolicyagent/opa:0.58.0 run --server

# Load policies (in production)
# curl -X PUT http://localhost:8181/v1/policies/gcc-authz --data-binary @policies/authz.rego
```

## Usage

### Option 1: Python Package
```python
from src.l3_m2_security_access_control import query_with_authorization

# Execute authorized query
result = query_with_authorization(
    query="Show Q3 revenue projections",
    user_id="alice@company.com",
    user_role="admin",
    user_namespace="admin-prod",
    target_namespace="finance-prod",
    context={"location": "US", "time": "business_hours"},
    pinecone_client=None,  # Your Pinecone client
    opa_client=None,  # Your OPA client
)

print(result)
# {
#   "status": "success",
#   "results": {...},
#   "audit_log": {...}
# }
```

### Option 2: FastAPI Server
```bash
# Start API server (Windows PowerShell)
.\scripts\run_api.ps1

# Or manually
uvicorn app:app --reload --port 8000
```

**API Documentation:** http://localhost:8000/docs

**API Endpoints:**

```bash
# Health check
curl http://localhost:8000/

# Authorized query
curl -X POST http://localhost:8000/query \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show Q3 revenue projections",
    "user_id": "alice@company.com",
    "user_role": "admin",
    "user_namespace": "admin-prod",
    "target_namespace": "finance-prod"
  }'

# Authorization check (pre-flight)
curl -X POST http://localhost:8000/authorize \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "bob@company.com",
    "user_role": "analyst",
    "user_namespace": "finance-prod",
    "target_namespace": "hr-prod",
    "action": "query"
  }'

# Create namespace (admin only)
curl -X POST http://localhost:8000/namespaces \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "marketing-prod",
    "business_unit": "Marketing",
    "region": "US"
  }'

# List accessible namespaces
curl http://localhost:8000/namespaces?user_id=bob@company.com&user_role=analyst

# Retrieve audit logs (compliance officer only)
curl http://localhost:8000/audit-logs?user_id=alice@company.com&limit=50
```

### Option 3: Jupyter Notebook
```bash
jupyter notebook notebooks/L3_M2_Security_Access_Control.ipynb
```

Interactive walkthrough with 12 sections covering all concepts.

## Testing

Run the comprehensive test suite:

```bash
# Windows PowerShell
.\scripts\run_tests.ps1

# Or manually
pytest -v tests/
```

**Test Coverage:**

The test suite includes **25+ tests** covering:

1. ✅ **RBAC Permission Checks:**
   - Admin full access to all namespaces
   - Analyst access to assigned namespace only
   - Analyst cross-tenant access denial (zero leakage)
   - Compliance officer read-all access
   - Unknown role denial

2. ✅ **Authorization Manager:**
   - Successful RBAC authorization
   - RBAC denial with reason
   - ABAC integration and policy evaluation
   - Combined RBAC+ABAC decisions

3. ✅ **Namespace Isolation:**
   - Namespace creation
   - User namespace listing by role
   - Database-level isolation enforcement

4. ✅ **Audit Trail:**
   - Immutable log entry creation
   - Successful access logging
   - Denied access logging
   - Timestamp-based write-once guarantee

5. ✅ **ABAC Policy Evaluation:**
   - OPA policy allow
   - OPA policy deny
   - Fail-safe denial when OPA unavailable

6. ✅ **JWT Token Validation:**
   - Successful token decode
   - Expired token handling
   - Invalid token rejection

7. ✅ **End-to-End Integration:**
   - Complete authorized query flow
   - Complete denied query flow with audit
   - Compliance officer cross-namespace access

8. ✅ **Security Matrix:**
   - Parametrized tests for all role × namespace combinations

**Sample Test Output:**
```
tests/test_m2_security_access_control.py::test_admin_full_access PASSED
tests/test_m2_security_access_control.py::test_analyst_same_namespace_access PASSED
tests/test_m2_security_access_control.py::test_analyst_cross_tenant_denial PASSED
tests/test_m2_security_access_control.py::test_compliance_officer_read_all PASSED
...

========================= 25 passed in 2.43s =========================
```

## Common Failures & Solutions

| Failure | Cause | Solution |
|---------|-------|----------|
| **Cross-Tenant Data Leak** | Missing namespace filter in Pinecone query | Always enforce `namespace=user_namespace` at query level. Verify in tests with `assert result["results"]["namespace"] == expected_namespace` |
| **Permission Denied (403)** | User role doesn't have required permission | Check `config.ROLE_PERMISSIONS` mapping. Verify JWT token contains correct `role` claim from M2.1 |
| **ABAC Policy Violations** | Context attributes (location, time) don't match OPA policy rules | Review Rego policy syntax. Test with `opa eval` CLI. Check context passed in request matches policy input schema |
| **JWT Token Expiration** | Token expired (default 30 min) | Implement token refresh flow from M2.1. Check `JWT_EXPIRATION_MINUTES` in config. Handle 401 errors gracefully in UI |
| **Audit Log Not Immutable** | PostgreSQL user has UPDATE/DELETE grants | Revoke: `REVOKE UPDATE, DELETE ON audit_logs FROM app_user`. Verify with `\dp audit_logs` in psql |
| **Namespace Assignment Race Condition** | Concurrent user creation with namespace assignment | Use database transactions. PostgreSQL: `BEGIN; INSERT INTO users ...; INSERT INTO user_namespaces ...; COMMIT;` |
| **Missing Namespace Isolation** | Pinecone query doesn't include namespace parameter | Pass `namespace=target_namespace` to `index.query()`. Test with cross-tenant queries and verify 0 matches |
| **OPA Connection Timeout** | OPA container not running or wrong URL | Check `docker ps | grep opa`. Verify `OPA_URL` in .env. Implement graceful fallback to RBAC-only mode |

## When to Use This Pattern

### ✅ Use Multi-Tenant Authorization When:

1. **Serving 20+ business units** on shared infrastructure (cost-effective vs. separate deployments)
2. **Regulatory compliance requires** mathematical proof of zero cross-tenant leakage (SOX, GDPR, DPDPA, HIPAA)
3. **Fine-grained permissions needed** beyond simple admin/user (e.g., read-only compliance access)
4. **Audit trail is mandatory** with immutability and long retention (7+ years)
5. **Context-aware access control** needed (location-based, time-based, device-based policies)

### ❌ Avoid This Pattern When:

1. **Single-tenant applications** (overhead not justified)
2. **<10 users** with simple access needs (basic role check sufficient)
3. **No compliance requirements** (simpler authorization may suffice)
4. **Performance is MORE critical than security** (namespace checks add latency)
5. **Rapid prototyping phase** (implement in production, not MVP)

## Decision Card

### Deployment Tier Recommendations

**Tier 1 - Basic RBAC (20-50 tenants)**
- **Cost:** ₹30,000-50,000/month (~$365-600 USD)
- **Features:**
  - RBAC with 3 roles (Admin, Analyst, Compliance Officer)
  - Pinecone namespace isolation
  - Basic audit logging (30-day retention)
  - PostgreSQL 15 on managed service (AWS RDS, Azure Database)
- **Use Case:** Small GCC deployments, single region
- **Performance:** <100ms query latency

**Tier 2 - Standard RBAC+ABAC (50-100 tenants)**
- **Cost:** ₹75,000-1,25,000/month (~$900-1,500 USD)
- **Features:**
  - All Tier 1 features
  - ABAC with Open Policy Agent
  - Advanced OPA policies (location, time, classification-based)
  - Compliance-grade audit logging (7-year retention)
  - Multi-region PostgreSQL replication
- **Use Case:** Medium GCC deployments, regulatory compliance (SOX, GDPR)
- **Performance:** <150ms query latency (OPA adds ~30ms)

**Tier 3 - Enterprise (100+ tenants)**
- **Cost:** ₹1,50,000+/month (~$1,800+ USD)
- **Features:**
  - All Tier 2 features
  - Custom ABAC policies per business unit
  - Real-time policy updates via GitOps
  - Advanced audit analytics and anomaly detection
  - 24/7 security monitoring and alerting
  - Multi-cloud deployment (AWS + Azure)
- **Use Case:** Large GCC enterprises, government agencies, financial institutions
- **Performance:** <200ms query latency with global distribution

### Cost Breakdown (Small GCC Example: 20 users, 50 tenants, 5K docs)

| Service | Tier | Monthly Cost (INR) | Monthly Cost (USD) |
|---------|------|-------------------:|-------------------:|
| Pinecone | Starter (1 pod) | ₹5,500 | $70 |
| PostgreSQL | RDS db.t3.small | ₹2,500 | $30 |
| OPA | Self-hosted (EC2 t3.micro) | ₹500 | $5 |
| **Total** | | **₹8,500** | **$105** |

*Free/open-source components: FastAPI, SQLAlchemy, pytest, Jupyter*

### GCC-Specific Considerations

1. **Data Residency:** Ensure Pinecone region matches GCC requirements (US, India, Singapore)
2. **Encryption:** Use M2.3 (Encryption & Secrets Management) for data-at-rest and in-transit
3. **Compliance Mapping:**
   - **SOX:** 7-year audit retention enforced
   - **GDPR:** Right to access (compliance officer queries), Right to erasure (admin namespace deletion)
   - **DPDPA (India):** Data localization via Pinecone India region
4. **Performance SLA:** 99.9% uptime with <200ms p95 query latency

## File Structure

```
gcc_comp_m2_v2/
├── app.py                              # FastAPI entrypoint with 6 endpoints
├── config.py                           # Environment & client management
├── requirements.txt                    # 15 pinned dependencies
├── .env.example                        # API key template (11 variables)
├── .gitignore                          # Python defaults + notebooks
├── LICENSE                             # MIT license
├── README.md                           # This file (comprehensive docs)
├── example_data.json                   # 4 users, 4 namespaces, 8 queries
├── example_data.txt                    # Test scenarios and ABAC contexts
│
├── src/                                # Source code package
│   └── l3_m2_security_access_control/  # Python package (importable)
│       └── __init__.py                 # 400+ lines: 3 classes, 7 functions
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M2_Security_Access_Control.ipynb  # 12 sections, interactive
│
├── tests/                              # Test suite
│   └── test_m2_security_access_control.py   # 25+ tests with mocking
│
├── configs/                            # Configuration files
│   └── example.json                    # Application settings
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API (PowerShell)
    └── run_tests.ps1                   # Windows: Run tests (PowerShell)
```

## Resources

- **Augmented Script:** [Augmented_GCC_Compliance_M2_2_Authorization_Multi.md](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M2_2_Authorization_Multi.md)
- **Pinecone Namespace Docs:** https://docs.pinecone.io/docs/namespaces
- **Open Policy Agent:** https://www.openpolicyagent.org/docs/latest/
- **FastAPI Security:** https://fastapi.tiangolo.com/tutorial/security/
- **PostgreSQL Row Security:** https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- **JWT Best Practices:** https://tools.ietf.org/html/rfc8725

## Next Steps

1. **Complete M2.3:** Encryption & Secrets Management (encrypt audit logs, manage JWT secrets)
2. **Implement Custom ABAC Policies:** Tailor OPA Rego policies for your business units
3. **Add Advanced Roles:** Define custom roles beyond Admin/Analyst/Compliance (e.g., Data Steward, Security Auditor)
4. **Integrate Enterprise IdP:** Connect to Okta, Azure AD, or AWS Cognito for SSO
5. **Deploy to Production:** Use Terraform/CloudFormation for infrastructure-as-code
6. **Monitor and Alert:** Set up Grafana dashboards for authorization metrics (allow/deny rates, latency)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Support

For issues or questions:
- Create an issue in the repository
- Consult the [augmented script](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M2_2_Authorization_Multi.md)
- Review [TVH Framework v2.0](https://techvoyagehub.com) documentation

---

**Generated from:** Augmented_GCC_Compliance_M2_2_Authorization_Multi.md
**Framework:** TVH L3 (Production-Ready)
**Service:** PINECONE + PostgreSQL + OPA
**Version:** 1.0.0
**Last Updated:** 2025-01-16
