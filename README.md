# L3 M1.2: Data Governance Requirements for RAG

## Overview

**Module:** M1 - Compliance Foundations for RAG Systems
**Video:** M1.2 - Data Governance Requirements for RAG
**Track:** GCC Compliance Basics
**Level:** L3 SkillElevate
**Duration:** 40-45 minutes

This production-ready codebase implements comprehensive data governance for RAG systems deployed in Global Capability Centers (GCCs), covering:

- **Data Classification** with PII/PHI/financial detection using Presidio
- **Complete Data Lineage** tracking across 7 interconnected systems
- **Automated Retention Policies** with legal compliance (GDPR, SOX, HIPAA)
- **Multi-Region Data Residency** controls (EU/India/US)
- **GDPR-Compliant Consent Management** with revocation workflows
- **Full GDPR Article 17** erasure request execution

## Real-World Problem

**GCC Case Study:** Fortune 500 parent company deployed RAG system for HR policy queries. When an employee submitted a GDPR Article 17 erasure request, the team discovered data scattered across 7 untracked systems. Unable to prove comprehensive deletion within the 30-day deadline, they faced a **€200,000 GDPR fine**.

**Key Insight:** *"Data governance is not a feature you add. It's an architecture you build."*

## What You'll Learn

1. Implement data classification schemes with PII/PHI/financial detection using Presidio
2. Design complete data lineage tracking across 7 RAG systems with immutable audit trails
3. Apply retention policies across all systems with automated deletion via Airflow
4. Configure data residency controls for multi-region GCCs (GDPR Article 44, DPDPA compliance)
5. Build consent management workflows with revocation mechanisms (GDPR Articles 6 & 7)
6. Execute GDPR Article 17 erasure requests with legal exception handling

## Concepts Covered

### 1. Data Classification
- **Sensitivity Levels:** Public, Internal, Confidential, Restricted
- **Data Types:** PII, PHI, Financial, Proprietary
- **Retention Requirements:**

| Data Type | Period | Regulation | Reason |
|-----------|--------|-----------|--------|
| HR Records | 7 years | FLSA, EEOC | Legal defense post-termination |
| Financial | 10 years | SOX 802 | Audit requirements |
| Medical | 7 years | HIPAA | Patient care continuity |
| Marketing Emails | 30 days | GDPR minimization | Campaign lifecycle |
| Audit Logs | 7 years | SOX, GDPR | Compliance verification |

### 2. Data Lineage
**7-Stage RAG Data Flow:**
1. Source Document → S3 upload
2. Chunks → Document split with chunk IDs
3. Embeddings → Via OpenAI with embedding IDs
4. Vector Storage → Pinecone namespace storage
5. Retrieval → User query with chunk tracking
6. Generation → LLM answer with generation ID
7. Caching → Redis with TTL
8. Analytics → BigQuery event logging

**Value:** Enables tracing and deletion across all interconnected systems.

### 3. Data Retention
- **Without policies:** Data accumulates indefinitely, violating GDPR data minimization
- **With policies:** Automated deletion via Airflow (e.g., "delete HR data older than 7 years")

### 4. Data Residency
**Requirements by Jurisdiction:**
- **GDPR (EU):** EU data must stay in EU (Article 44) - requires adequacy decisions or SCCs for transfers
- **DPDPA (India):** Sensitive data can transfer with consent; government may designate must-stay-in-India types
- **PIPL (China):** Critical data must remain in China; transfer requires security assessment

### 5. Consent Management
**GDPR Consent Requirements (Articles 6 & 7):**
- Freely given (no coercion)
- Specific (clear purpose defined)
- Informed (user knows data handling)
- Unambiguous (affirmative action required)
- Withdrawable (revocation mechanism available)

### 6. Data Subject Rights (GDPR Chapter 3)
1. **Right to Access (Article 15):** Export all personal data
2. **Right to Rectification (Article 16):** Fix incorrect data
3. **Right to Erasure (Article 17):** Delete all data (with legal exceptions)
4. **Right to Data Portability (Article 20):** Machine-readable export
5. **Right to Object (Article 21):** Opt-out from processing

## Architecture

### Technology Stack

#### Layer 1: Data Classification & Detection
- **Presidio** (Microsoft PII detection): 50+ PII types, 95%+ accuracy, multi-language
- **spaCy NLP Engine:** Named entity recognition (PERSON, ORG, LOCATION, DATE)
- **Custom Rules:** Domain-specific patterns (employee IDs, policy numbers, financial markers)

#### Layer 2: Data Lineage & Audit Trails
- **PostgreSQL Audit Tables:** Immutable append-only logs, 7-10 year retention
- **Vector Database Metadata:** Pinecone namespaces with metadata tags
- **Schema:** `{source_id, chunk_id, embedding_id, retrieval_id, generation_id, timestamp}`

#### Layer 3: Retention Policy Engine
- **Apache Airflow:** Scheduled retention jobs, DAG orchestration
- **TTL Configurations:** Redis (30 days), S3 lifecycle policies (90 days), CloudWatch logs (7 years)
- **Capacity:** Handles 10K+ deletion operations/day

#### Layer 4: Consent Management
- **Database Schema:** `user_consent (user_id, data_type, purpose, consent_date, revocation_date, legal_basis)`
- **FastAPI Endpoints:** `/consent/grant`, `/consent/revoke`, `/consent/status`
- **Performance:** <50ms response time

#### Layer 5: Multi-System Integration (7 Systems)
1. Vector Database (embeddings)
2. Document Store (S3/GCS)
3. Application Logs (CloudWatch/ELK)
4. Backup Systems (S3 Glacier)
5. Cache Layer (Redis)
6. Generation History (PostgreSQL)
7. Analytics Database (BigQuery/Snowflake)

#### Layer 6: Data Residency (Multi-Region GCCs)
- **Regional Infrastructure:** Frankfurt (eu-central-1), Mumbai (ap-south-1), N. Virginia (us-east-1)
- **Compliance Rules:** GDPR Article 44 (EU data in EU), DPDPA (India data in India)

### Cost Considerations
- **Small GCC:** ~₹25K/month + setup
- **Large GCC:** ~₹4L/month across 3 regions

## Prerequisites

- Python 3.11+
- **Presidio** (local PII detection - requires spaCy models)
- **OpenAI** API access (optional - for embeddings)
- **Pinecone** account (optional - for vector database)
- PostgreSQL database (for audit trails)
- Apache Airflow (for retention policies)
- Redis (for caching)

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/yesvisare/gcc_comp_ai_ccc_l2.git
cd gcc_comp_ai_ccc_l2
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install spaCy Model (Required for Presidio)
```bash
python -m spacy download en_core_web_lg
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 6. Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PRESIDIO_ENABLED` | Yes | Enable/disable Presidio PII detection (true/false) |
| `OPENAI_ENABLED` | No | Enable OpenAI embeddings (true/false) |
| `OPENAI_API_KEY` | No | OpenAI API key (if OPENAI_ENABLED=true) |
| `PINECONE_ENABLED` | No | Enable Pinecone vector database (true/false) |
| `PINECONE_API_KEY` | No | Pinecone API key (if PINECONE_ENABLED=true) |
| `PINECONE_ENVIRONMENT` | No | Pinecone environment (if PINECONE_ENABLED=true) |
| `DATABASE_URL` | Yes | PostgreSQL connection string for audit trails |
| `REDIS_URL` | No | Redis connection string (default: redis://localhost:6379) |
| `AIRFLOW_ENABLED` | No | Enable automated retention policies (true/false) |
| `AIRFLOW_HOME` | No | Airflow installation path |
| `EU_REGION` | No | AWS region for EU data residency (default: eu-central-1) |
| `INDIA_REGION` | No | AWS region for India data residency (default: ap-south-1) |
| `US_REGION` | No | AWS region for US data residency (default: us-east-1) |

## Usage

### Run API Server

**Windows PowerShell:**
```powershell
.\scripts\run_api.ps1
```

**Linux/Mac:**
```bash
PYTHONPATH=. uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Access API documentation at: `http://localhost:8000/docs`

### Run Tests

**Windows PowerShell:**
```powershell
.\scripts\run_tests.ps1
```

**Linux/Mac:**
```bash
PYTHONPATH=. pytest -q tests/
```

### Interactive Notebook
```bash
jupyter notebook notebooks/L3_M1_Compliance_Foundations_RAG_Systems.ipynb
```

## API Endpoints

### Health & Info
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with API information |
| `/health` | GET | Detailed health check with service status |

### Data Classification
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/classify` | POST | Classify document and detect PII/PHI/financial data |

### Lineage Tracking
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/lineage/document` | POST | Track Stage 1: Document upload |
| `/lineage/chunks` | POST | Track Stage 2: Document chunking |
| `/lineage/embedding` | POST | Track Stage 3: Embedding generation |
| `/lineage/vector` | POST | Track Stage 4: Vector storage |
| `/lineage/retrieval` | POST | Track Stage 5: Chunk retrieval |
| `/lineage/generation` | POST | Track Stage 6: LLM generation |
| `/lineage/cache` | POST | Track Stage 7: Response caching |
| `/lineage/{source_id}` | GET | Get complete lineage chain |

### Retention Policies
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/retention/check/{source_id}` | GET | Check retention compliance |
| `/retention/{source_id}` | DELETE | Execute retention-based deletion |
| `/retention/schedule` | POST | Schedule Airflow retention job |

### Data Residency
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/residency/validate` | POST | Validate data residency compliance |
| `/residency/route/{country_code}` | GET | Route data to compliant region |

### Consent Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/consent/grant` | POST | Grant user consent (GDPR Article 6/7) |
| `/consent/revoke` | DELETE | Revoke user consent (GDPR Article 7(3)) |
| `/consent/check` | GET | Check consent for specific purpose |
| `/consent/{user_id}` | GET | Get all user consents (GDPR Article 15) |

### GDPR Article 17 Erasure
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/erasure/validate` | POST | Validate erasure request against legal exceptions |
| `/erasure/{user_id}` | DELETE | Execute complete erasure across all systems |
| `/erasure/verify/{user_id}` | GET | Verify complete erasure |
| `/erasure/certificate/{user_id}` | GET | Generate deletion certificate |

## Directory Structure

```
gcc_comp_ai_ccc_l2/
├── src/l3_m1_compliance_foundations_rag_systems/  # Core package
│   └── __init__.py                                 # Business logic (6 components)
├── app.py                                          # FastAPI application
├── config.py                                       # Configuration & client management
├── requirements.txt                                # Dependencies
├── .env.example                                    # Environment template
├── .gitignore                                      # Git ignore rules
├── LICENSE                                         # MIT License
├── README.md                                       # This file
├── example_data.json                               # Sample JSON data
├── example_data.txt                                # Sample text data
├── notebooks/                                      # Jupyter notebooks
│   └── L3_M1_Compliance_Foundations_RAG_Systems.ipynb
├── tests/                                          # Test suite
│   └── test_m1_compliance_foundations_rag_systems.py
├── configs/                                        # Configuration files
│   └── example.json
└── scripts/                                        # Automation scripts
    ├── run_api.ps1                                 # Windows: Start API
    └── run_tests.ps1                               # Windows: Run tests
```

## Common Failures & Solutions

| Failure | Root Cause | Solution |
|---------|------------|----------|
| **Incomplete deletion** | Data remains in cache/backups post-erasure | Implement cross-system lineage tracking; verify deletion in all 7 systems including backups |
| **Untracked lineage** | Cannot locate which embeddings came from which source | Track every transformation stage with unique IDs; maintain immutable audit trail |
| **Purpose creep** | Data used beyond original consent scope | Enforce consent checks at retrieval time; block queries with purpose mismatch |
| **Cross-region data leakage** | EU personal data stored outside EU | Implement residency validation before storage; use regional routing based on user location |
| **Retention policy gaps** | Employee data retained after 7-year requirement | Schedule automated Airflow DAGs; regularly audit data age against legal limits |
| **Consent withdrawal delays** | Data continues processing after revocation | Implement real-time consent checks; immediately block access upon revocation |

## When NOT to Use This

This comprehensive governance system may be **overkill** for:

- **Single-region, single-tenant RAG** with no cross-border data transfers
- **Public data only** scenarios (no PII/PHI/financial data)
- **Limited regulatory exposure** (not subject to GDPR/SOX/HIPAA/DPDPA)
- **Early MVP stage** with <100 users and no enterprise deployment plans
- **Non-production research projects** without real user data

**Use lightweight alternatives:** Basic logging + manual deletion scripts + single-region deployment

## Decision Card

### Use this comprehensive governance approach when:

✅ **Multi-region GCC** serving 50+ business units
✅ **Operating under 2+ regulatory jurisdictions** (US/EU/India)
✅ **Processing HR, financial, or health-related data** (high sensitivity)
✅ **Anticipating GDPR/SOX/DPDPA audits** within next 12 months
✅ **Handling classified data** requiring strict access controls
✅ **Enterprise deployment** with >1000 users and long-term retention needs

### Don't use when:

❌ Single-region deployment with public data only
❌ Early MVP stage (<6 months to production)
❌ Limited regulatory exposure (no GDPR/SOX/HIPAA requirements)
❌ Small user base (<100 users) with no growth plans
❌ Research/academic projects without real user data

### Cost Estimates:

- **Small GCC (1 region, <5000 documents):** ~₹25K/month + ₹50K setup
- **Medium GCC (2 regions, <50K documents):** ~₹1.5L/month + ₹2L setup
- **Large GCC (3 regions, >100K documents):** ~₹4L/month + ₹5L setup

*Includes Presidio (free), OpenAI embeddings, Pinecone, PostgreSQL, Airflow, regional infrastructure*

## GCC Context

### Why Data Governance Matters for GCCs:

1. **Parent company liability:** US/EU parent companies are liable for GCC data handling
2. **Cross-border transfers:** GCC data often flows between India/EU/US, triggering GDPR Article 44
3. **Multi-jurisdiction compliance:** Must comply with GDPR (EU), DPDPA (India), SOX (US), HIPAA (US)
4. **Audit scrutiny:** GCCs face regular audits from parent company compliance teams
5. **Employee data:** HR data retention must comply with strictest local law (often 7 years)
6. **Financial data:** SOX 802 requires 10-year retention for financial records

### GCC-Specific Considerations:

- **Data residency:** EU employee data cannot leave EU without SCCs; India may require local storage
- **Consent management:** GDPR consent differs from DPDPA consent (stricter withdrawal requirements)
- **Right to be forgotten:** Must execute erasure within 30 days across all global systems
- **Audit trails:** Immutable logs required for both SOX and GDPR compliance verification

## Testing

The test suite covers:

- ✅ **Unit tests** for all 6 core components
- ✅ **Integration tests** for API endpoints
- ✅ **Compliance tests** (GDPR Article 17, retention policies, data residency)
- ✅ **Security tests** (cross-tenant isolation, encryption validation)

```bash
# Run all tests with coverage
pytest tests/ -v --cov=src

# Run specific test category
pytest tests/ -k "test_classification"
pytest tests/ -k "test_gdpr"
```

## PractaThon Connection

**Mission:** Build a production-ready data governance layer for your GCC's existing RAG system.

**Objectives:**
1. Implement Presidio-based PII detection across all ingested documents
2. Create PostgreSQL audit trail schema for lineage tracking
3. Deploy Airflow DAGs for automated retention policy enforcement
4. Configure multi-region routing based on user location (EU/India/US)
5. Build GDPR Article 17 erasure workflow with cross-system deletion

**Deliverables:**
- Working API with all governance endpoints
- Jupyter notebook demonstrating full workflow
- Test suite with >80% coverage
- Documentation for compliance team review

## Resources

- **Augmented Script:** [View on GitHub](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M1_2_Data_G.md)
- **GDPR Full Text:** https://gdpr.eu/
- **DPDPA 2023:** https://www.meity.gov.in/dpdpa-2023
- **Presidio Documentation:** https://microsoft.github.io/presidio/
- **SOX Section 802:** https://www.soxlaw.com/s802.htm
- **HIPAA Privacy Rule:** https://www.hhs.gov/hipaa/

## License

MIT License - See LICENSE file for details.

Copyright (c) 2025 yesvisare

## Support

For questions or issues:

- Review the [augmented script](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M1_2_Data_G.md)
- Check existing [GitHub issues](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/issues)
- Contact: support@techvoyagehub.com

---

**Built with TechVoyageHub L3 SkillElevate Standards**
**Compliance-Ready • Production-Grade • GCC-Optimized**
