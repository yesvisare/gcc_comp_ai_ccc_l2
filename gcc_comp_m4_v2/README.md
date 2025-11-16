# L3 M4.2: Vendor Risk Assessment

A comprehensive vendor risk assessment framework for Global Capability Centers (GCCs) managing third-party compliance in RAG systems. Evaluates vendors using a 5-category weighted matrix to prevent vendor-caused data breaches and ensure regulatory compliance.

**Part of:** TechVoyageHub L3 Production RAG Engineering Track
**Prerequisites:**
- Generic CCC Level 1 (M1-M4)
- GCC Compliance M1.1-M1.2 (Compliance Foundations)
- GCC Compliance M2.1-M2.3 (Security & Access Control)
- GCC Compliance M3.1-M3.3 (Monitoring & Incident Response)
- GCC Compliance M4.1 (Model Cards & Documentation)

**Processing Mode:** OFFLINE (Local processing only - no external LLM/vector database services)

## What You'll Build

A production-ready vendor risk assessment platform that:

1. **Evaluates third-party vendors** using a 5-category risk matrix:
   - Security (30%): SOC 2, ISO 27001, penetration testing, incident history
   - Privacy (25%): GDPR compliance, DPA availability, data handling policies
   - Compliance (20%): Industry certifications, audit reports, regulatory alignment
   - Reliability (15%): SLA guarantees, uptime metrics, support responsiveness
   - Data Residency (10%): Geographic locations, subprocessors, cross-border transfers

2. **Automates DPA (Data Processing Agreement) review** for 12 essential GDPR clauses

3. **Tracks subprocessors** through the supply chain with change detection

4. **Enables continuous monitoring** of vendor certifications, incidents, and compliance changes

**Key Capabilities:**
- **Risk Scoring:** Calculate 0-100 risk scores with weighted category evaluation
- **Automated Approval:** Low Risk (90-100) = Approved; Critical Risk (<50) = Rejected
- **DPA Clause Detection:** Semantic similarity matching for missing clauses (optional feature)
- **Subprocessor Registry:** Track vendors' vendors and their compliance status
- **Multi-Format Reporting:** Excel, DataFrame, JSON outputs for CFO/auditor presentations
- **GCC-Specific:** Handles multi-jurisdictional requirements (GDPR, DPDPA, CCPA, SOX)

**Success Criteria:**
- Assess 20+ vendors with consistent, auditable methodology
- Identify missing DPA clauses before signing contracts
- Prevent vendor-caused breaches (Capital One-style: $80M+ fines)
- Satisfy auditor requirements (GDPR Article 28, SOX, ISO 27001)
- Scale vendor management (50-200 third parties tracked automatically)

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    VENDOR RISK ASSESSMENT                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   COLLECT VENDOR DATA                   │
        │   • SOC 2 reports, ISO 27001 certs      │
        │   • DPAs, audit reports                 │
        │   • SLA metrics, uptime data            │
        │   • Data center locations               │
        │   • Subprocessor lists                  │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   5-CATEGORY WEIGHTED EVALUATION        │
        │                                         │
        │   Security (30%)     ┌──────────┐       │
        │   Privacy (25%)      │ 0-100    │       │
        │   Compliance (20%)   │ Score    │       │
        │   Reliability (15%)  │ Per      │       │
        │   Data Residency(10%)│ Category │       │
        │                      └──────────┘       │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   WEIGHTED AVERAGE CALCULATION          │
        │   Overall = Σ(Category × Weight)        │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   RISK LEVEL DETERMINATION              │
        │   90-100: LOW RISK → APPROVED           │
        │   70-89:  MEDIUM RISK → CONDITIONS      │
        │   50-69:  HIGH RISK → MITIGATIONS       │
        │   0-49:   CRITICAL RISK → REJECTED      │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   REPORTING & CONTINUOUS MONITORING     │
        │   • Excel reports for CFO               │
        │   • Quarterly re-evaluation alerts      │
        │   • Certification expiration tracking   │
        │   • Subprocessor change notifications   │
        └─────────────────────────────────────────┘
```

## Quick Start

### 1. Clone and Setup
```bash
git clone <repo_url>
cd gcc_comp_m4_v2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)
```bash
cp .env.example .env
# Edit .env if needed (all features work offline by default)
```

### 4. Run Tests
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; pytest -v

# Or use script
./scripts/run_tests.ps1

# Linux/Mac
PYTHONPATH=$PWD pytest -v
```

### 5. Start API
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; uvicorn app:app --reload

# Or use script
./scripts/run_api.ps1

# Linux/Mac
PYTHONPATH=$PWD uvicorn app:app --reload
```

API will be available at:
- **API Endpoint:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 6. Explore Notebook
```bash
jupyter lab notebooks/L3_M4_Enterprise_Integration_Governance.ipynb
```

## API Usage Examples

### Assess a Vendor

```bash
curl -X POST "http://localhost:8000/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "OpenAI",
    "soc2_date": "2024-06-15",
    "iso27001": true,
    "pentest_date": "2024-10-01",
    "breaches_count": 0,
    "gdpr_compliant": true,
    "dpa_available": true,
    "data_policy_score": 3,
    "deletion_process": "automated_verified",
    "access_controls": "strong",
    "certifications": ["soc2", "iso27001"],
    "audit_date": "2024-07-15",
    "notification_process": "proactive",
    "violations_count": 0,
    "sla_guarantee": 99.9,
    "actual_uptime_12m": 99.95,
    "support_response_time": "<1h",
    "dr_plan": "tested_annually",
    "dc_locations": ["US", "EU", "Asia"],
    "dc_selectable": true,
    "subproc_locations": ["US", "EU"],
    "sccs_available": true,
    "localization_support": "full"
  }'
```

**Response:**
```json
{
  "vendor": "OpenAI",
  "overall_score": 92.5,
  "risk_level": "LOW RISK",
  "recommendation": "APPROVED - Low risk vendor, suitable for production use",
  "category_scores": {
    "security": 95.0,
    "privacy": 90.0,
    "compliance": 88.5,
    "reliability": 91.0,
    "data_residency": 87.5
  },
  "findings": {
    "security": [
      "✓ SOC 2 Type II current (issued 6 months ago)",
      "✓ ISO 27001 certified",
      "✓ Recent penetration test (3 months ago)",
      "✓ No security breaches in past 3 years"
    ],
    ...
  }
}
```

### Get Assessment Report

```bash
curl "http://localhost:8000/report"
```

**Response:**
```json
{
  "vendors": [
    {
      "Vendor": "OpenAI",
      "Overall Score": 92.5,
      "Risk Level": "LOW RISK",
      "Security": 95.0,
      "Privacy": 90.0,
      "Compliance": 88.5,
      "Reliability": 91.0,
      "Data Residency": 87.5,
      "Recommendation": "APPROVED - Low risk vendor, suitable for production use"
    }
  ],
  "total_vendors": 1
}
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `DATABASE_URL` | No | None | PostgreSQL URL for vendor registry (optional - stores in memory if not set) |
| `USE_DPA_ANALYSIS` | No | `false` | Enable sentence-transformers for DPA clause detection (optional feature) |
| `REPORT_OUTPUT_DIR` | No | `./reports` | Directory for Excel/PDF report generation |

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| **DPA Without Essential Clauses** | Vendor provides DPA but missing subprocessor approval clause | Use automated DPA clause checker before signing (enable `USE_DPA_ANALYSIS=true`); Flag missing clauses to legal team |
| **Vendor Certification Lapses Undetected** | Vendor's SOC 2 expired 6 months ago, still in use | Implement continuous monitoring; Set quarterly re-evaluation alerts; Track certification expiration dates |
| **Subprocessor Supply Chain Breach** | Vendor A uses Vendor B, Vendor B uses Vendor C, Vendor C breached - your data exposed through unmonitored chain | Maintain subprocessor registry at all levels; Audit subprocessor's risk scores using same framework; Require vendors to notify before adding new subprocessors |
| **Vendor with Multiple Breaches (Automatic Rejection)** | Vendor has 3 security breaches in past 3 years; Security score = 0/100; Overall score ~30 (CRITICAL RISK) | Reject vendor - multiple breaches indicate pattern of security failures; No amount of compliance makes up for breach history; Seek alternative vendor |
| **Expired SOC 2 Report (>24 months old)** | Vendor's SOC 2 report is 30 months old; Security category scores 15/100 | Request updated SOC 2 Type II report (<12 months); Place vendor on probation until renewal; Consider downgrade to lower-risk use cases only |
| **Missing GDPR DPA for EU Data** | Vendor claims GDPR compliance but no signed DPA; Privacy category scores 20/100 | CANNOT use vendor for EU personal data (GDPR Article 28 violation); Request DPA immediately; Pause processing until DPA signed |
| **SLA Violations (Actual < Committed)** | Vendor committed 99.9% SLA but delivered 98.5%; Reliability category scores low | Invoke SLA breach penalties; Request root cause analysis and remediation plan; Consider vendor replacement if pattern continues |
| **Unknown Subprocessor Locations** | Vendor won't disclose where subprocessors store data; Data Residency category scores 0/100 | Escalate to vendor senior management; Data residency compliance REQUIRES transparency; Reject vendor if disclosure not provided |
| **Regulatory Violations (Historical Fines)** | Vendor has 2 regulatory violations in past 5 years; Compliance category deducts 20 points | Understand nature of violations (minor vs. major); Require vendor to demonstrate remediation; Additional monitoring if approved; May be disqualifying for highly regulated industries |
| **No Disaster Recovery Plan** | Vendor has no documented DR/BC plan; Reliability category loses 10 points | Request DR/BC plan documentation; Require annual testing; For mission-critical systems, may be disqualifying; Consider vendor as lower-tier/non-critical only |

## Decision Card

### WHEN TO USE
- **Pre-procurement evaluation** - Before signing contracts with new vendors
- **Quarterly re-evaluation** - Existing vendors (certifications expire, incidents occur)
- **Compliance requirement changes** - New regulations (DPDPA in India, GDPR updates)
- **Security incident investigations** - Determine if vendor contributed to breach
- **External audit preparation** - SOX, ISO 27001, GDPR compliance reviews
- **Vendor contract renewals** - Re-assess before renewing multi-year agreements
- **Subprocessor additions** - Vendor wants to add new third-party subprocessor
- **Cross-border data transfers** - Evaluate data residency compliance

### WHEN NOT TO USE
- **Internal teams** - Framework is for third-party vendors, not your own security team
- **Vendors already rejected by executive team** - Framework supports decisions, doesn't override business judgment
- **Legal contract review replacement** - Framework assists attorneys, doesn't replace legal review
- **Point solutions already approved** - If vendor is mandated by parent company (e.g., Microsoft 365), assessment is informational only
- **Open source libraries** - Use SBOM/dependency scanning tools instead (different risk model)
- **One-time/low-risk vendors** - Overkill for vendors with no data access (e.g., office supplies)

### KEY TRADE-OFFS

| Decision | Trade-Off | Implication |
|----------|-----------|-------------|
| **High Security Weight (30%)** | Vendor with excellent privacy/compliance but older SOC 2 may score low despite strong overall posture | Reflects reality: breaches are most common third-party risk; Acceptable false positives to avoid false negatives |
| **Automated DPA Checker** | NLP-based clause detection imperfect (threshold >0.8 similarity); May miss complex conditional clauses | Always require attorney final review; Flag suspicious clauses; Tool assists but doesn't replace legal expertise |
| **Continuous Monitoring** | Requires data collection infrastructure (APIs, web scraping, manual tracking); High effort for vendors without public compliance data | High effort justified by early warning system; Prevents "certification expired unnoticed" scenarios; Scale benefit: 50 vendors monitored for ₹10K/month vs. 2 FTE analysts at ₹1.34Cr/month |
| **All-or-Nothing SLA Thresholds** | Vendor with 99.85% SLA (just below 99.9% threshold) drops to medium score despite minimal difference (1.3 hours/year) | Consider business context: Is 5.7 hours downtime (99.85%) vs. 4.38 hours (99.9%) truly unacceptable for your use case? Use judgment for edge cases |
| **Subprocessor Deep Dive** | Creates compliance burden: asking vendors to list all subprocessors, update when they change; Some vendors resist disclosure | GDPR Article 28(4) REQUIRES it anyway; Non-negotiable for EU data; Vendor resistance may indicate poor governance (red flag) |
| **Weighted vs. Unweighted Scoring** | Security gets 30% weight, Data Residency only 10%; Vendor excellent at data residency but weak security still scores poorly | Aligns with real-world risk: Security breaches far more common than data residency violations; Adjust weights if your industry differs (financial services may increase compliance weight) |
| **Breach History Penalties** | 3 breaches = -30 points from Security category; Vendor with strong current controls still penalized for past failures | Past breaches predict future risk; Multiple breaches indicate systemic issues, not one-off mistakes; Justified to prevent "we've fixed it" claims without proof |

### COST VS. BENEFIT

**Costs:**
- **Implementation:** 40-60 hours (database design, scoring logic, API development, testing)
- **Infrastructure:** ₹10,000/month ($120) - PostgreSQL RDS (₹5K), S3 storage (₹2K), Grafana Cloud (₹3K)
- **Ongoing Monitoring:** 5-10 hours/month (review alerts, update vendor data, quarterly re-assessments)
- **Training:** 4-8 hours for compliance team to learn framework

**Benefits:**
- **Breach Prevention:** Avoid Capital One-style vendor breaches ($80M OCC fine + $190M settlement)
- **Audit Compliance:** Satisfy GDPR Article 28, SOX Section 404, ISO 27001 Annex A.15.1.1 requirements
- **Scale Efficiency:** Replace 2 FTE analysts (₹1.34Cr/month) with automation (₹10K/month)
- **Early Warning:** Catch certification lapses, incidents before they affect production systems
- **Risk Quantification:** CFO-ready reports showing cost-vs-risk trade-offs for vendor decisions
- **Supply Chain Visibility:** Track 50-200 third parties automatically vs. manual spreadsheets

**ROI Calculation:**
- **Year 1 Cost:** ₹1.2L implementation + ₹1.2L infrastructure + ₹60K-1.2L monitoring = ₹2.4L-3.6L total
- **Year 1 Benefit (Conservative):** Prevent 1 medium vendor breach (₹2Cr incident response, regulatory fine, customer notification) = ₹2Cr saved
- **ROI:** 5.5× to 8× in year one
- **Year 1 Benefit (Scale Efficiency):** Replace 2 FTE analysts (₹16L/year) = ₹16L saved
- **ROI:** 4.4× to 6.7× from efficiency alone

**Break-even:** If framework prevents even ONE vendor-caused incident costing >₹3.6L, it pays for itself.

**Payback Period:** 2-3 months (assumes continuous operation prevents incidents quarterly)

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'src.l3_m4_enterprise_integration_governance'`, ensure:

```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD

# Linux/Mac
export PYTHONPATH=$PWD
```

### Tests Failing
Run tests with verbose output to see detailed error messages:

```bash
pytest -v tests/
```

Common test failures:
- **Missing dependencies:** Run `pip install -r requirements.txt`
- **Date format errors:** Ensure date strings use ISO format (`YYYY-MM-DD`)
- **Pandas version conflicts:** Upgrade pandas: `pip install --upgrade pandas`

### API Errors

**500 Internal Server Error:**
- Check logs for detailed error messages
- Verify all required fields in request body
- Ensure date fields use ISO format strings

**422 Validation Error:**
- Missing required fields in request body
- Invalid field values (e.g., `sla_guarantee` must be float 0-100)
- Check API docs at `/docs` for field requirements

### Database Connection Issues
If using optional PostgreSQL database:
- Verify `DATABASE_URL` format: `postgresql://user:password@host:port/database`
- Test connection: `psql $DATABASE_URL`
- Check firewall rules if remote database

### DPA Analysis Issues
If enabling optional DPA clause detection (`USE_DPA_ANALYSIS=true`):
- First run downloads sentence-transformers models (~100MB)
- May take 1-2 minutes on first use
- Requires internet connection for initial model download only

## Architecture Details

### Technology Stack

**Core Framework:**
- **Python 3.9+** - Language
- **FastAPI** - REST API framework
- **Pydantic** - Data validation
- **pandas** - Risk score calculations, reporting
- **pytest** - Testing framework

**Optional Components:**
- **PostgreSQL** - Vendor registry storage (production deployments)
- **sentence-transformers** - DPA clause detection (local NLP model)
- **pdfplumber** - PDF parsing for DPA analysis
- **openpyxl** - Excel report generation
- **requests** - Vendor status API integration

**No External Services Required:**
- ✅ Operates entirely offline
- ✅ No LLM API calls (OpenAI, Anthropic)
- ✅ No vector database (Pinecone, Qdrant)
- ✅ No cloud dependencies (AWS, GCP, Azure)

### Database Schema (Optional)

If using PostgreSQL (`DATABASE_URL` configured):

```sql
-- vendors table
CREATE TABLE vendors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    website VARCHAR(255),
    services TEXT,
    risk_score DECIMAL(5,2),
    last_reviewed TIMESTAMP,
    dpa_signed BOOLEAN DEFAULT FALSE
);

-- risk_assessments table
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER REFERENCES vendors(id),
    assessment_date TIMESTAMP DEFAULT NOW(),
    security_score DECIMAL(5,2),
    privacy_score DECIMAL(5,2),
    compliance_score DECIMAL(5,2),
    reliability_score DECIMAL(5,2),
    data_residency_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    risk_level VARCHAR(50),
    recommendation TEXT
);

-- dpa_clauses table
CREATE TABLE dpa_clauses (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER REFERENCES vendors(id),
    clause_name VARCHAR(255),
    present BOOLEAN,
    reviewed_date TIMESTAMP
);

-- subprocessors table
CREATE TABLE subprocessors (
    id SERIAL PRIMARY KEY,
    parent_vendor_id INTEGER REFERENCES vendors(id),
    subprocessor_name VARCHAR(255),
    service VARCHAR(255),
    risk_score DECIMAL(5,2)
);

-- vendor_incidents table
CREATE TABLE vendor_incidents (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER REFERENCES vendors(id),
    incident_date DATE,
    incident_type VARCHAR(100),
    severity VARCHAR(50),
    resolution_date DATE
);
```

## Integration with Other Modules

### M4.1 Model Cards
- Auto-populate vendor registry from "Third-Party Dependencies" section
- Extract vendor names, services, versions from model card metadata
- Trigger vendor assessment when new dependency added

### M3.2 Audit Logs
- Cross-reference vendor access logs with risk assessments
- Alert when high-risk vendor accesses sensitive data
- Generate audit trail for vendor risk decisions

### M2.1 Secrets Management
- Ensure vendor API keys stored in Vault, not hardcoded
- Verify vendor API key rotation policies
- Audit which teams have access to vendor credentials

### Generic CCC Deployment
- Pull actual vendor usage metrics from production systems
- Monitor vendor API call volumes, error rates, latency
- Feed real uptime data into reliability scoring

## Next Module

**GCC Compliance M4.3: Change Management & Compliance**

**Prerequisites Satisfied by This Module:**
- ✅ Understand vendor risk assessment framework
- ✅ Can evaluate vendors using 5-category matrix
- ✅ Can identify missing DPA clauses
- ✅ Can track subprocessors through supply chain

**How M4.3 Builds On This:**
- When vendor changes (contract modification, new subprocessor), trigger change management process
- Compliance change = re-evaluate risk score, update documentation, notify stakeholders
- Integrate with M4.1 model cards: update "Third-Party Dependencies" section when vendor status changes
- Implement approval workflows for vendor risk level changes (LOW → MEDIUM requires approval)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contributing

This module is part of the TechVoyageHub L3 Production RAG Engineering Track. For contributions or issues, please follow the track's contribution guidelines.

## Acknowledgments

- **GDPR Article 28** - Data Processing Agreement requirements
- **NIST Cybersecurity Framework** - Risk assessment methodology
- **SOC 2 Trust Service Criteria** - Security evaluation standards
- **ISO 27001** - Information security management
- **Real-world breach case studies:** Capital One (2019), Facebook-Cambridge Analytica (2018), SolarWinds (2020), MOVEit (2023)
