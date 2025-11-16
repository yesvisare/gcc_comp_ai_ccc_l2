# L3 M3.3: Audit Logging & SIEM Integration

Production-ready implementation of comprehensive audit logging for RAG systems with SIEM integration, designed for GCC (Global Capability Center) environments requiring regulatory compliance.

## Overview

This module provides **immutable audit trail** capabilities for RAG (Retrieval-Augmented Generation) systems operating in regulated environments. It captures all critical operations (query, retrieval, generation, access control) with cryptographic hash chaining, PostgreSQL storage, optional AWS S3 archival, and real-time SIEM integration.

**Key Distinction:** Application logs answer "Is my system healthy?" Audit logs answer "Can I prove compliance to a regulator?"

## Concepts Covered

1. **Audit Logging vs. Application Logging** - Understanding the fundamental differences in purpose, retention, and immutability requirements
2. **Six Critical Audit Points in RAG Systems** - Query input, access control decision, retrieval, LLM generation, response delivery, and error handling
3. **Immutability Strategies** - PostgreSQL Row-Level Security (RLS), AWS S3 Object Lock, and cryptographic hash chaining
4. **Correlation ID Architecture** - Multi-tenant tracking with nested correlation for GCC environments (tenant_id, correlation_id, span_id)
5. **SIEM Integration Patterns** - Splunk HEC, Elasticsearch direct indexing, and Datadog Logs API integration
6. **Tiered Retention Policies** - Hot/warm/cold storage strategy for 7-10 year compliance requirements (SOX, HIPAA, GDPR)
7. **Structured JSON Logging** - Event schema design for regulatory compliance and security operations
8. **Multi-Tenant Audit Isolation** - Tenant-specific audit queries and compliance reporting

## Features

- ✅ **Comprehensive Event Capture** - Log all RAG operations with structured JSON schema
- ✅ **Cryptographic Integrity** - SHA-256 hash chaining for tamper detection
- ✅ **Immutable Storage** - PostgreSQL RLS + optional S3 Object Lock (COMPLIANCE mode, 7-year retention)
- ✅ **Multi-Tenant Support** - Tenant-isolated audit trails with correlation ID hierarchy
- ✅ **SIEM Integration** - Real-time streaming to Splunk, Elasticsearch, or Datadog
- ✅ **RESTful API** - FastAPI endpoints for logging, querying, and integrity verification
- ✅ **Regulatory Compliance** - Meets SOX Section 404, GDPR Article 15, HIPAA 164.312(b), PCI-DSS Req 10
- ✅ **Production-Ready** - Type hints, comprehensive tests, error handling, and monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Application                          │
│  (Query → Retrieval → Generation → Response)               │
└──────────────────┬──────────────────────────────────────────┘
                   │ Audit Events
                   ▼
┌─────────────────────────────────────────────────────────────┐
│               Audit Logger (Core Module)                    │
│  • CorrelationContext (tenant_id, correlation_id, span_id) │
│  • AuditEvent (event_type, data, hash_chain)               │
│  • Cryptographic SHA-256 hash linking                      │
└─────────┬───────────────┬────────────────┬──────────────────┘
          │               │                │
          ▼               ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│ PostgreSQL   │  │ AWS S3       │  │ SIEM Platform    │
│ (RLS)        │  │ Object Lock  │  │ (Splunk/ELK/DD)  │
│ Hot Storage  │  │ Cold Archive │  │ Real-time SOC    │
└──────────────┘  └──────────────┘  └──────────────────┘
```

**Log Volume Calculation:**
- 1,000 queries/day → ~9,000 audit events/day (6 events per RAG request)
- At 2KB per event → 18MB daily, 6.6GB yearly, **46GB for 7-year SOX retention**

## Prerequisites

- Python 3.9+
- PostgreSQL 13+ (for immutable audit log storage)
- (Optional) AWS account with S3 (for long-term archival)
- (Optional) SIEM platform: Splunk, Elasticsearch, or Datadog
- (Recommended) Virtual environment for dependency isolation

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yesvisare/gcc_comp_ai_ccc_l2.git
cd gcc_comp_ai_ccc_l2/gcc_comp_m3_v3
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials and optional cloud integrations
```

### 5. Setup PostgreSQL Database

```bash
# Create database
createdb audit_logs

# Create user (example)
psql -c "CREATE USER audit_user WITH PASSWORD 'your_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE audit_logs TO audit_user;"
```

The schema will be auto-created on first API startup, or you can initialize manually:

```python
from config import get_config
from src.l3_m3_monitoring_reporting_compliance import create_audit_logger

config = get_config()
logger = create_audit_logger(config)
logger.postgres_store.create_schema()
```

## Usage

### Start API Server

**Linux/Mac:**
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Windows PowerShell:**
```powershell
.\scripts\run_api.ps1
```

API will be available at:
- **Base URL:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs (Swagger UI)
- **OpenAPI Spec:** http://localhost:8000/redoc

### Run Tests

**Linux/Mac:**
```bash
pytest tests/ -v
```

**Windows PowerShell:**
```powershell
.\scripts\run_tests.ps1
```

### Interactive Notebook

```bash
jupyter notebook notebooks/L3_M3_Monitoring_Reporting_Compliance.ipynb
```

## API Endpoints

### Health Check

Check system status and configuration.

```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "audit_logging_siem",
  "version": "1.0.0",
  "postgres_enabled": true,
  "s3_enabled": false,
  "siem_enabled": false,
  "siem_platform": null
}
```

### Log Audit Event

Create immutable audit log entry with hash chaining.

```bash
POST /audit/log
Content-Type: application/json

{
  "event_type": "RAG_QUERY",
  "user_id": "emp-5678",
  "user_role": "analyst",
  "user_department": "finance",
  "tenant_id": "finance",
  "data": {
    "query": "What were Q4 2024 revenue figures?",
    "client_ip": "10.0.1.45"
  },
  "data_classification": "CONFIDENTIAL",
  "compliance_flags": ["SOX_RELEVANT"]
}

Response:
{
  "event_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "timestamp": "2024-11-16T12:34:56.789Z",
  "event_type": "RAG_QUERY",
  "correlation_id": "req-abc123def456",
  "current_hash": "a3d5f7e9...",
  "status": "logged"
}
```

### Query Audit Logs

Search audit trail with flexible filters.

```bash
POST /audit/query
Content-Type: application/json

{
  "tenant_id": "finance",
  "user_id": "emp-5678",
  "event_type": "RAG_QUERY",
  "start_time": "2024-11-01T00:00:00Z",
  "end_time": "2024-11-30T23:59:59Z",
  "limit": 100
}

Response:
{
  "count": 42,
  "events": [ /* array of matching events */ ],
  "query": { /* echo of query params */ }
}
```

### Verify Hash Chain

Check tamper-detection integrity for a tenant.

```bash
GET /audit/verify/finance

Response:
{
  "tenant_id": "finance",
  "status": "chain_valid",
  "total_events": 15234,
  "message": "Hash chain integrity verified - no tampering detected"
}

# If tampering detected:
{
  "tenant_id": "finance",
  "status": "chain_broken",
  "total_events": 15234,
  "broken_links": [
    {
      "position": 512,
      "prev_event_id": "...",
      "curr_event_id": "...",
      "expected_hash": "abc123...",
      "actual_hash": "def456..."
    }
  ],
  "message": "Found 1 broken hash links - possible tampering!"
}
```

### Get Audit Statistics

Retrieve audit summary for a tenant.

```bash
GET /audit/stats/finance

Response:
{
  "tenant_id": "finance",
  "total_events": 15234,
  "events_by_type": {
    "RAG_QUERY": 2500,
    "RAG_RETRIEVAL": 2500,
    "RAG_GENERATION": 2500,
    "ACCESS_CONTROL": 450,
    "ERROR": 84
  },
  "top_users": {
    "emp-5678": 1234,
    "emp-9012": 987
  },
  "time_range": {
    "earliest": "2024-01-01T00:00:00Z",
    "latest": "2024-11-16T12:34:56Z"
  }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| **Database (Required)** ||||
| `DB_HOST` | PostgreSQL host | `localhost` | Yes |
| `DB_PORT` | PostgreSQL port | `5432` | Yes |
| `DB_NAME` | Database name | `audit_logs` | Yes |
| `DB_USER` | Database user | `audit_user` | Yes |
| `DB_PASSWORD` | Database password | - | Yes |
| **Logging** ||||
| `LOG_FILE_PATH` | Log file location | `/var/log/rag/audit.log` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| **Immutability** ||||
| `IMMUTABILITY_MODE` | Strategy (postgresql/s3/hybrid) | `postgresql` | No |
| `ENABLE_HASH_CHAIN` | Enable SHA-256 linking | `true` | No |
| **AWS S3 (Optional)** ||||
| `AWS_ENABLED` | Enable S3 archival | `false` | No |
| `AWS_ACCESS_KEY_ID` | AWS access key | - | If AWS enabled |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | If AWS enabled |
| `S3_BUCKET_NAME` | S3 bucket for archives | - | If AWS enabled |
| `S3_RETENTION_DAYS` | Retention period | `2555` (7 years) | No |
| **SIEM (Optional)** ||||
| `SIEM_ENABLED` | Enable SIEM integration | `false` | No |
| `SIEM_PLATFORM` | Platform (splunk/elasticsearch/datadog) | `splunk` | If SIEM enabled |
| `SPLUNK_HEC_URL` | Splunk HTTP Event Collector URL | - | If Splunk |
| `SPLUNK_HEC_TOKEN` | Splunk HEC token | - | If Splunk |
| `ELASTICSEARCH_URL` | Elasticsearch endpoint | - | If Elasticsearch |
| `ELASTICSEARCH_API_KEY` | Elasticsearch API key | - | If Elasticsearch |
| `DATADOG_API_KEY` | Datadog API key | - | If Datadog |
| **Multi-Tenant** ||||
| `TENANT_ID` | Default tenant ID | `default_tenant` | No |
| `ENABLE_MULTI_TENANT` | Enable multi-tenancy | `false` | No |
| **Retention Policy** ||||
| `HOT_STORAGE_DAYS` | Recent logs in PostgreSQL | `90` | No |
| `WARM_STORAGE_DAYS` | Intermediate logs in S3 Standard | `365` | No |
| `COLD_STORAGE_DAYS` | Archive logs in S3 Glacier | `2555` (7 years) | No |

### Deployment Modes

**1. Offline Mode (Local Only):**
- PostgreSQL with RLS for immutability
- No cloud dependencies
- Suitable for on-premise deployments

**2. AWS Hybrid Mode:**
- PostgreSQL (hot storage 90 days)
- S3 archival with Object Lock (7-year retention)
- Cost-effective long-term compliance

**3. Full SIEM Integration:**
- PostgreSQL + S3 archival
- Real-time streaming to Splunk/ELK/Datadog
- Enterprise security operations center (SOC) monitoring

## Common Failures & Solutions

| Failure Mode | Symptoms | Root Cause | Solution |
|--------------|----------|------------|----------|
| **Missing Audit Trail** | Cannot answer auditor questions about data access | No logging at critical RAG pipeline points | Implement comprehensive logging at: query input, access control, retrieval, generation, response, errors |
| **Log Tampering Undetected** | Gaps in audit logs, regulators assume fraud | Logs stored in mutable database without immutability controls | Use append-only storage (PostgreSQL RLS), S3 Object Lock, or cryptographic hash chains |
| **Slow Audit Investigation** | 60+ minutes to answer compliance questions | No correlation IDs linking events together | Generate unique correlation_id at request start; pass through entire RAG pipeline |
| **SIEM Integration Failure** | Security team cannot monitor RAG system centrally | Logs not forwarded to enterprise SIEM platform | Configure log forwarder (Splunk UF, Elasticsearch, Datadog agent) to send structured JSON logs |
| **Undetected Anomalies** | Insider threats, bulk data exports not caught | No real-time analysis of access patterns | Deploy SIEM correlation rules for: unusual query volumes, after-hours access, privilege escalation attempts |
| **Storage Cost Overrun** | Logs consume excessive disk space | Keeping all logs in "hot" storage tier indefinitely | Implement tiered retention: hot (30 days), warm (365 days), cold (1-10 years per regulation) |

## Decision Card

### When to Use This Approach

✅ **Organization Profile:**
- Operating in regulated industries: healthcare (HIPAA), finance (SOX), payments (PCI-DSS), EU operations (GDPR)
- Enterprise GCC serving 10+ internal tenants or external clients
- Handling classified/confidential data requiring audit proof
- Subject to compliance audits (annual or ad-hoc)

✅ **Technical Profile:**
- Production RAG system processing 100+ queries/day
- Multiple user roles with differentiated access levels
- Integration with centralized security operations center (SOC)
- Long-term data retention requirements (6-10 years)

✅ **Risk Tolerance:**
- Non-compliance fines exceed logging implementation cost (generally true for regulated industries)
- Regulatory audit failure unacceptable to business
- Need to prove compliance status to external auditors/board

### When NOT to Use

❌ **Skip Full Audit Logging If:**
- Internal research project with synthetic/test data only
- Single-user RAG system (no multi-tenant complexity)
- Non-regulated industry with no audit requirements
- Short-lived proof-of-concept (expected lifespan <6 months)
- Zero external compliance obligations

❌ **Defer SIEM Integration If:**
- Organization has no existing SIEM infrastructure
- Security team does not exist or cannot monitor logs
- Budget severely constrained and basic database logging suffices
- Compliance requirements only require log retention, not real-time monitoring

### Trade-Offs

**Storage Approach Comparison:**

| Approach | Cost | Immutability Strength | Query Speed | Setup Complexity |
|----------|------|----------------------|-------------|------------------|
| PostgreSQL RLS | $$ (database licensing) | Medium (policy-enforced) | Fast (direct SQL) | Low |
| S3 Object Lock | $ (cloud storage) | Very High (cryptographic) | Slow (retrieval) | Medium |
| Hash Chain | $ (minimal cost) | Very High (mathematical proof) | Medium (verification) | High |

**SIEM Platform Considerations:**

| Platform | Cost | Best For | Integration Complexity |
|----------|------|----------|------------------------|
| Splunk | ~$150/GB/year | Large enterprises, complex correlation | Medium (Universal Forwarder) |
| Elasticsearch (ELK) | Self-hosted cost | Organizations with ops teams | High (requires tuning) |
| Datadog | ~$15/host/month | Cloud-native shops, simplicity | Low (Python agent) |
| Azure Sentinel | ~$2.50/GB ingested | Microsoft ecosystem | Low (native integration) |

## Development

### Project Structure

```
gcc_comp_m3_v3/
├── app.py                              # FastAPI entrypoint
├── config.py                           # Environment & client management
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # Environment variable template
├── .gitignore                          # Python defaults
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Sample audit events
├── example_data.txt                    # Sample queries
│
├── src/                                # Source code package
│   └── l3_m3_monitoring_reporting_compliance/
│       └── __init__.py                 # Core audit logging logic
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M3_Monitoring_Reporting_Compliance.ipynb
│
├── tests/                              # Test suite
│   └── test_m3_monitoring_reporting_compliance.py
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API
    └── run_tests.ps1                   # Windows: Run tests
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test class
pytest tests/test_m3_monitoring_reporting_compliance.py::TestAuditEvent -v
```

### Code Quality

```bash
# Linting
flake8 src/ tests/ --max-line-length=100

# Type checking
mypy src/ --ignore-missing-imports

# Formatting
black src/ tests/ --line-length=100
```

## Regulatory Compliance References

This implementation addresses requirements from:

- **SOX Section 404:** Immutable audit trails for financial systems
- **GDPR Article 15:** Right to access (correlation IDs support user data requests)
- **HIPAA 164.312(b):** Audit controls and log integrity requirements
- **PCI-DSS Requirement 10:** Access logging and data exfiltration tracking
- **ISO 27001 A.12.4:** Logging and monitoring requirements

## Learning Resources

- **Interactive Notebook:** `notebooks/L3_M3_Monitoring_Reporting_Compliance.ipynb` - Step-by-step walkthrough with examples
- **Augmented Script:** [GCC_Compliance_M3_3_Audit_Logging_SIEM_Int.md](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M3_3_Audit_Logging_SIEM_Int.md)
- **API Documentation:** http://localhost:8000/docs (when server running)
- **Example Data:** See `example_data.json` and `example_data.txt` for sample audit events and queries

## Production Deployment Checklist

- [ ] Configure PostgreSQL with Row-Level Security (RLS) policies
- [ ] Set strong `DB_PASSWORD` in production `.env`
- [ ] Enable AWS S3 archival with Object Lock (COMPLIANCE mode)
- [ ] Configure SIEM integration (Splunk/ELK/Datadog)
- [ ] Set up tiered retention policy (hot/warm/cold)
- [ ] Create separate database roles: `audit_app` (INSERT only), `audit_admin` (SELECT for archival)
- [ ] Enable SSL/TLS for database connections
- [ ] Configure API rate limiting and authentication
- [ ] Set up monitoring and alerting for audit system health
- [ ] Test hash chain verification on sample data
- [ ] Document incident response procedures for broken hash chains
- [ ] Schedule annual compliance audit trail review

## Support

For issues, questions, or contributions:

1. Review the interactive notebook for usage examples
2. Check the augmented script for detailed implementation guidance
3. Open an issue in the repository with detailed reproduction steps

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Version History

- **v1.0.0** (2025-11-16): Initial production release
  - Core audit logging with PostgreSQL RLS
  - Optional S3 archival with Object Lock
  - SIEM integration (Splunk, Elasticsearch, Datadog)
  - Cryptographic hash chaining
  - Multi-tenant correlation ID support
  - RESTful API with FastAPI
  - Comprehensive test suite

---

**Built with PractaThon™ standards for TechVoyageHub's GCC Compliance curriculum.**
