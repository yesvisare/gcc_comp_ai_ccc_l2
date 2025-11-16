# L3 M2.3: Encryption & Secrets Management

Production-ready implementation of HashiCorp Vault integration for dynamic secrets retrieval, AES-256 encryption at rest, TLS 1.3 encryption in transit, and automated key rotation for multi-tenant RAG systems under GCC (Governance, Compliance, Control) framework.

**Part of:** TechVoyageHub L3 Production RAG Engineering Track
**Prerequisites:** Generic CCC M1-M4 (Functional RAG MVP), GCC Compliance M2.1-M2.2 (AuthN/AuthZ)
**SERVICE:** HashiCorp Vault (primary) with OpenAI/Pinecone credential management
**Duration:** 40-45 minutes

## What You'll Build

A fully encrypted, compliance-ready secrets management system serving **50+ business units across 3 regions** (India, US, EU) with zero hardcoded credentials. This module implements the security foundation for GCC's multi-tenant RAG system, ensuring SOX 404, DPDPA, and GDPR compliance.

**Key Capabilities:**
- **Dynamic Secrets Retrieval:** HashiCorp Vault integration with Kubernetes ServiceAccount authentication (no hardcoded credentials)
- **AES-256 Encryption at Rest:** Envelope encryption for Pinecone vectors, PostgreSQL metadata, and Redis caches
- **TLS 1.3 Encryption in Transit:** Automated certificate management via cert-manager + Let's Encrypt
- **Automated Key Rotation:** Quarterly for API keys (OpenAI, Pinecone), daily for database credentials
- **Multi-Region Compliance:** SOX 404 (7-year audit trails), DPDPA (India data residency), GDPR (EU data protection)
- **Immutable Audit Logging:** All secret access and key rotation events logged to S3 Glacier

**Success Criteria:**
- Zero hardcoded secrets in codebase (all credentials retrieved from Vault)
- All sensitive data encrypted with AES-256 before storage
- TLS 1.3 enforced for all external connections (RAG→OpenAI, RAG→Pinecone, RAG→PostgreSQL)
- Automated key rotation with zero service downtime
- SOC 2, ISO 27001, SOX 404 audit requirements met

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     Multi-Tenant RAG System                      │
│                    (50+ Business Units, 3 Regions)               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Pod (rag-api)                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. ServiceAccount Token → Vault Authentication             │ │
│  │    (24-hour TTL, pod identity verification)                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                │                                 │
│                                ▼                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 2. VaultClient Retrieves Secrets:                          │ │
│  │    • OpenAI API key (quarterly rotation)                   │ │
│  │    • Pinecone API key (quarterly rotation)                 │ │
│  │    • PostgreSQL dynamic creds (24-hour TTL)                │ │
│  │    • KEK for envelope encryption (annual rotation)         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   OpenAI API     │  │  Pinecone Vector │  │   PostgreSQL     │
│   (TLS 1.3)      │  │  DB (TLS 1.3)    │  │   (TLS 1.3 +     │
│                  │  │  AES-256 built-in│  │   TDE + pgcrypto)│
│ Embeddings for   │  │                  │  │                  │
│ 50+ tenants      │  │ Tenant isolation │  │ Metadata storage │
└──────────────────┘  └──────────────────┘  └──────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│            Encryption at Rest (Envelope Encryption)              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ DEK (Data Encryption Key) → Encrypts sensitive data        │ │
│  │ KEK (Key Encryption Key)  → Encrypts DEK (from Vault)      │ │
│  │ Stored: encrypted_dek || iv || ciphertext || tag           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              Compliance Audit Trail (Immutable)                  │
│  • S3 Glacier with legal hold (7-year retention for SOX 404)    │
│  • Multi-region replication (India, US, EU for data residency)  │
│  • Events: secret_access, key_rotation, encryption_request      │
└─────────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. **Pod Authentication:** K8s ServiceAccount token proves identity to Vault
2. **Secret Retrieval:** Vault verifies with K8s API, returns time-limited client token
3. **Credential Access:** Application retrieves OpenAI/Pinecone/PostgreSQL credentials
4. **Encryption:** Sensitive data encrypted with AES-256 using KEK from Vault
5. **TLS in Transit:** All external API calls use TLS 1.3 with automated cert rotation
6. **Audit Logging:** All events logged to immutable S3 Glacier storage

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/yesvisare/gcc_comp_ai_ccc_l2.git
cd gcc_comp_ai_ccc_l2/gcc_comp_m2_v3
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and configure Vault settings
```

**For Development (No Vault):**
```bash
# .env
VAULT_ENABLED=false
OFFLINE=true
```

**For Production (With Vault):**
```bash
# .env
VAULT_ENABLED=true
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=your-vault-token  # Or use K8s ServiceAccount auth
```

### 4. Run Tests
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; pytest -v tests/

# Or use script
./scripts/run_tests.ps1
```

### 5. Start API
```bash
# Windows PowerShell
$env:VAULT_ENABLED='False'; $env:PYTHONPATH=$PWD; uvicorn app:app --reload

# Or use script
./scripts/run_api.ps1
```

**API Endpoints:**
- `GET /` - Health check
- `POST /secrets/retrieve` - Retrieve secret from Vault
- `GET /secrets/openai` - Get OpenAI API key
- `GET /secrets/pinecone` - Get Pinecone API key
- `POST /encrypt` - Encrypt data with AES-256
- `POST /decrypt` - Decrypt AES-256 data
- `GET /tls/status` - Check certificate expiry
- `POST /keys/rotate` - Rotate API key
- `POST /keys/rotate-postgres` - Rotate PostgreSQL credentials

### 6. Explore Notebook
```bash
jupyter lab notebooks/L3_M2_Security_Access_Control.ipynb
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VAULT_ENABLED` | No | `false` | Enable HashiCorp Vault integration |
| `VAULT_ADDR` | If Vault enabled | `http://localhost:8200` | Vault server URL |
| `VAULT_TOKEN` | If Vault enabled (dev) | - | Static token for development |
| `VAULT_NAMESPACE` | No | `gcc-secrets` | Vault namespace for secrets |
| `VAULT_K8S_ROLE` | If K8s auth | `rag-api` | Kubernetes role for ServiceAccount auth |
| `OPENAI_ENABLED` | No | `false` | Enable OpenAI client (fallback) |
| `OPENAI_API_KEY` | If OpenAI enabled | - | OpenAI API key (fallback when Vault disabled) |
| `PINECONE_ENABLED` | No | `false` | Enable Pinecone client (fallback) |
| `PINECONE_API_KEY` | If Pinecone enabled | - | Pinecone API key (fallback) |
| `POSTGRES_HOST` | No | `localhost` | PostgreSQL host (fallback) |
| `POSTGRES_PASSWORD` | If Postgres enabled | - | PostgreSQL password (fallback) |
| `TLS_ENABLED` | No | `false` | Enable TLS certificate management |
| `CERT_PATH` | If TLS enabled | `/etc/tls/certs` | Directory containing cert.pem |
| `OFFLINE` | No | `false` | Run in offline mode (notebook) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| **Hardcoded secrets in GitHub** (Bangalore Case: $50M funding lost) | Developers committed .env file with API keys; attackers incurred $120K mining costs; CTO/CFO terminated | Install git-secrets pre-commit hook; use Vault dynamic secrets; enable GitHub secret scanning |
| **Unencrypted database backups** | PostgreSQL backups stored in S3 without encryption; GDPR/DPDPA violation | Enable PostgreSQL TDE + pgcrypto; use S3 SSE-KMS encryption; verify backup encryption in deployment checklist |
| **Expired TLS certificates** | Manual cert renewal process missed; 4-hour production outage | Deploy cert-manager with Let's Encrypt automation; monitor cert expiry with alerts 30 days before |
| **Missed key rotation schedule** | Manual rotation process forgotten; SOC 2 audit failure | Use KeyRotationManager automated rotation; quarterly for APIs, daily for DB creds via Vault dynamic secrets |
| **Vault authentication failures** | ServiceAccount token expired or invalid K8s role binding | Verify K8s role binding: `kubectl get serviceaccount rag-api`; check Vault policy allows secret access |
| **Insufficient audit logging** | Missing events for secret access, key rotation; SOX 404 compliance failure | Implement audit_log_entry() for ALL operations; send to S3 Glacier with 7-year retention |
| **Single-region Vault deployment** | Data residency violation for DPDPA (India), GDPR (EU) | Deploy multi-region Vault with active-active replication; route requests to regional Vault clusters |
| **Weak encryption keys** | Used hardcoded KEK or insufficient key length | Retrieve KEK from Vault; use 32-byte (256-bit) keys; rotate KEK annually |

## Decision Card

### When to Use This Approach

- **Multi-tenant systems** serving 50+ business units requiring strict tenant isolation
- **Cross-regional deployments** needing data residency compliance (India DPDPA, EU GDPR)
- **Production systems** with SOC 2, ISO 27001, or SOX 404 audit requirements
- **Regulated industries** (finance, healthcare) requiring encryption at rest and in transit
- **Systems handling PII/PHI** requiring AES-256 encryption and immutable audit trails
- **Microservices in Kubernetes** needing dynamic, short-lived credentials
- **API-heavy architectures** with multiple third-party integrations (OpenAI, Pinecone, etc.)
- **Organizations with compliance teams** requiring 7-year audit log retention

### When NOT to Use

- **Simple single-tenant applications** without compliance requirements (over-engineered)
- **Development/prototype environments** where hardcoded secrets are acceptable risk
- **Systems without regulatory requirements** (no SOX, GDPR, HIPAA, PCI-DSS)
- **Small teams** (< 5 people) without dedicated ops/security resources
- **Non-Kubernetes deployments** where Vault integration complexity outweighs benefits
- **Monolithic applications** without microservices architecture
- **Open-source projects** where all credentials are expected to be user-provided

### Trade-offs

**Complexity:**
- **High initial setup cost:** Vault cluster deployment (3-node HA), cert-manager, K8s integration
- **Learning curve:** Understanding Vault auth methods, secret engines, RBAC policies
- **Operational overhead:** Monitoring Vault health, backup/disaster recovery planning

**Cost:**
- **Infrastructure:** Vault cluster VMs/containers (~$500-1000/month for 3-node HA)
- **Pinecone:** $0.096/GB-month for serverless (built-in AES-256)
- **S3 Glacier:** ~$0.004/GB-month for 7-year audit log retention
- **Certificate automation:** Free with Let's Encrypt + cert-manager

**Latency:**
- **Secret retrieval:** +20-50ms per Vault API call (cached after first request)
- **Encryption overhead:** +5-10ms per AES-256 operation (minimal for small payloads)
- **TLS handshake:** +10-30ms per connection (reused with keep-alive)

**Benefits:**
- **Zero hardcoded secrets:** Eliminates #1 cause of security breaches ($50M funding loss case)
- **Automated rotation:** Quarterly API keys, daily DB creds with zero downtime
- **Audit compliance:** SOC 2, ISO 27001, SOX 404 certification ready
- **Multi-region support:** Data residency for DPDPA, GDPR without code changes

## Architecture Details

### Vault Integration (Kubernetes ServiceAccount Auth)

**Authentication Flow:**
1. Pod starts with K8s ServiceAccount mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`
2. VaultClient reads JWT token from ServiceAccount
3. Vault verifies JWT with K8s API server (trusted endpoint)
4. Vault returns client token with 24-hour TTL and RBAC policies
5. Client token used for all subsequent secret requests
6. Token auto-renewed before expiration; invalidated on pod termination

**Vault Configuration (Production):**
```hcl
# Kubernetes auth method
vault auth enable kubernetes

vault write auth/kubernetes/config \
    kubernetes_host="https://kubernetes.default.svc" \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# RBAC policy for rag-api
vault policy write rag-api-policy - <<EOF
path "gcc-secrets/data/openai" {
  capabilities = ["read"]
}
path "gcc-secrets/data/pinecone" {
  capabilities = ["read"]
}
path "gcc-secrets/data/postgres" {
  capabilities = ["read"]
}
path "gcc-secrets/data/encryption/kek" {
  capabilities = ["read"]
}
EOF

# Bind policy to K8s ServiceAccount
vault write auth/kubernetes/role/rag-api \
    bound_service_account_names=rag-api \
    bound_service_account_namespaces=production \
    policies=rag-api-policy \
    ttl=24h
```

### Envelope Encryption (AES-256-GCM)

**Encryption Process:**
1. Generate random DEK (Data Encryption Key): 32 bytes
2. Generate random IV (Initialization Vector): 16 bytes
3. Encrypt plaintext with DEK using AES-256-GCM → ciphertext + auth tag
4. Encrypt DEK with KEK (Key Encryption Key from Vault) using AES-256-ECB
5. Concatenate: `encrypted_dek (32) || iv (16) || ciphertext (variable) || tag (16)`
6. Base64 encode result for storage/transmission

**Decryption Process:**
1. Base64 decode encrypted data
2. Extract components: encrypted_dek, iv, ciphertext, tag
3. Decrypt DEK with KEK from Vault
4. Decrypt ciphertext with DEK using AES-256-GCM + tag verification
5. Return plaintext

**Security Properties:**
- **Authenticated encryption:** GCM mode provides confidentiality + integrity
- **Random IV:** Different ciphertext for same plaintext (prevents pattern analysis)
- **Key separation:** KEK stored in Vault, DEK ephemeral (never persisted unencrypted)
- **Key rotation:** Rotate KEK annually, re-encrypt all DEKs with new KEK

### TLS Certificate Automation (cert-manager + Let's Encrypt)

**Certificate Lifecycle:**
1. cert-manager monitors Certificate resources in K8s
2. Creates ACME challenge with Let's Encrypt
3. Let's Encrypt validates domain ownership (HTTP-01 or DNS-01)
4. cert-manager stores certificate in K8s Secret
5. Init container mounts Secret to pod at `/etc/tls/certs`
6. Application loads cert.pem and key.pem on startup
7. cert-manager renews 30 days before expiry (zero downtime)

**Configuration:**
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: rag-api-tls
  namespace: production
spec:
  secretName: rag-api-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - rag-api.gcc.techvoyagehub.com
  renewBefore: 720h  # 30 days
```

## GCC Compliance Requirements

### SOX 404 (Sarbanes-Oxley)
- **7-year immutable audit trail:** All secret access, key rotation, encryption events
- **Storage:** S3 Glacier with legal hold (prevents deletion)
- **Format:** JSON logs with digital signatures for integrity verification
- **Events tracked:** secret_access, api_key_rotation, postgres_credential_rotation, encryption_request

### DPDPA (Digital Personal Data Protection Act - India)
- **Data residency:** India user data stored in India region only
- **Implementation:** Multi-region Vault replication with request routing
- **Vault cluster:** vault-india.gcc.internal for India operations
- **Encryption:** AES-256 for all PII/sensitive data

### GDPR (General Data Protection Regulation - EU)
- **Right to be forgotten:** Ability to delete user data on request
- **Encryption at rest:** AES-256 for all EU citizen data
- **Data residency:** EU user data stored in EU region
- **Vault cluster:** vault-eu.gcc.internal for EU operations

### SOC 2 Type II
- **Access controls:** RBAC policies in Vault limit secret access
- **Audit logging:** All secret access logged with user/pod identity
- **Key rotation:** Documented quarterly rotation for API keys
- **Encryption verification:** Deployment checklist validates encryption enabled

### ISO 27001
- **Information security management:** Vault provides centralized secret management
- **Incident response:** Audit logs enable forensic investigation
- **Risk assessment:** Regular key rotation reduces exposure window

## Deployment Checklist (Production)

**Pre-Deployment:**
- [ ] Vault cluster deployed (3-node HA with auto-unseal)
- [ ] Kubernetes auth method configured
- [ ] RBAC policies created for all services
- [ ] Secrets populated in Vault (OpenAI, Pinecone, PostgreSQL, KEK)
- [ ] cert-manager installed with Let's Encrypt ClusterIssuer
- [ ] PostgreSQL TDE enabled + pgcrypto extension loaded
- [ ] S3 Glacier bucket created for audit logs (legal hold enabled)

**Verification:**
- [ ] Run `vault status` - confirm sealed=false, HA enabled
- [ ] Test K8s ServiceAccount auth: `vault login -method=kubernetes role=rag-api`
- [ ] Verify secret access: `vault kv get gcc-secrets/openai`
- [ ] Check certificate valid: `openssl x509 -in /etc/tls/certs/cert.pem -text`
- [ ] Test encryption roundtrip: encrypt → decrypt → verify plaintext match
- [ ] Confirm audit logs flowing to S3 Glacier
- [ ] Run key rotation test: rotate OpenAI key, verify zero downtime

**Post-Deployment:**
- [ ] Monitor Vault metrics (Prometheus + Grafana)
- [ ] Set up alerts for certificate expiry (30 days threshold)
- [ ] Schedule quarterly API key rotation (add to ops calendar)
- [ ] Document incident response process
- [ ] Conduct SOC 2 / ISO 27001 readiness review

## Troubleshooting

### Vault Disabled Mode
The module will run without Vault integration if `VAULT_ENABLED=false` in `.env`. The `config.py` file will skip Vault client initialization, and API endpoints will return service unavailable responses. This is the default behavior for local development/testing.

To enable Vault:
```bash
# .env
VAULT_ENABLED=true
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=dev-root-token-uuid  # Dev only
```

### Import Errors
If you see `ModuleNotFoundError: No module named 'src.l3_m2_security_access_control'`, ensure:
```bash
$env:PYTHONPATH=$PWD  # Windows PowerShell
export PYTHONPATH=$PWD  # Linux/Mac
```

### Tests Failing
Run tests with verbose output:
```bash
pytest -v tests/
```

Common issues:
- **hvac not installed:** `pip install hvac==2.1.0`
- **Vault not running:** Tests skip Vault-dependent tests automatically
- **Cryptography errors:** `pip install cryptography==41.0.7`

### Vault Authentication Failures
**Symptom:** `PermissionError: Vault authentication failed - invalid token`

**Diagnosis:**
```bash
# Check Vault status
vault status

# Verify token
vault token lookup

# Check K8s ServiceAccount
kubectl get serviceaccount rag-api
kubectl describe role rag-api
```

**Fix:**
- Verify `VAULT_TOKEN` is valid (dev mode)
- Confirm K8s ServiceAccount exists and bound to Vault role
- Check Vault RBAC policy allows secret access

### Certificate Expiry Warnings
**Symptom:** `Certificate expires in X days` (X < 30)

**Fix:**
```bash
# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Force renewal
kubectl annotate certificate rag-api-tls cert-manager.io/issue-temporary-certificate=true

# Verify renewal
kubectl describe certificate rag-api-tls
```

## Real-World Case Study: Bangalore GCC $50M Loss

**Background:**
In 2024, a Bangalore-based GCC (Global Capability Center) lost $50M Series B funding due to hardcoded secrets exposed on GitHub for 18 months. Attackers discovered the credentials and incurred $120K in cryptocurrency mining costs on the company's cloud infrastructure.

**Timeline:**
- **Month 0:** Developer committed `.env` file with OpenAI API key to public GitHub repo
- **Month 18:** Attacker discovered credentials via automated GitHub scanning
- **Month 18 + 1 week:** $120K in unauthorized usage (cryptocurrency mining)
- **Month 18 + 2 weeks:** Series B investors discovered security breach during due diligence
- **Month 18 + 1 month:** $50M funding round cancelled; CTO and CFO terminated

**Root Causes:**
1. Hardcoded secrets in version control (no git-secrets hook)
2. No secret rotation (same key for 18 months)
3. Insufficient audit logging (breach detected only after investor review)
4. No cost alerts on cloud provider

**Prevention with This Module:**
- ✅ **Vault integration:** No secrets in code/version control
- ✅ **Quarterly key rotation:** Exposure window reduced to 90 days maximum
- ✅ **Immutable audit logs:** All API key usage logged to S3 Glacier
- ✅ **Cost monitoring:** Cloud provider alerts for unusual usage patterns

## Learning Outcomes

After completing this module, you will:

1. **Integrate HashiCorp Vault** for dynamic credential retrieval with Kubernetes ServiceAccount authentication
2. **Configure AES-256 encryption at rest** for vector databases (Pinecone) and relational databases (PostgreSQL) using envelope encryption
3. **Implement TLS 1.3 encryption in transit** with automated certificate management via cert-manager + Let's Encrypt
4. **Build automated key rotation** (quarterly for API keys, daily for database credentials) with zero service downtime
5. **Understand GCC compliance requirements** (SOX 404, DPDPA, GDPR) and implement 7-year immutable audit trails
6. **Deploy production-ready secrets management** for multi-tenant RAG systems serving 50+ business units across 3 regions
7. **Recognize common security failures** (hardcoded secrets, unencrypted backups, manual key rotation) and implement prevention measures

## Next Module

**L3 M2.4: Rate Limiting & DDoS Protection**
Implement token bucket rate limiting, IP-based throttling, and distributed rate limiting with Redis for GCC's multi-tenant RAG system.

## License

MIT License - see [LICENSE](LICENSE) for details

## Support

For issues or questions:
- Open an issue: https://github.com/yesvisare/gcc_comp_ai_ccc_l2/issues
- TechVoyageHub L3 Track: https://techvoyagehub.com/l3-production-rag
