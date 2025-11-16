# L3 M4.2: Vendor Risk Assessment

Production-ready implementation of comprehensive vendor risk assessment for GCC (Global Capability Centers) compliance systems.

## Overview

This module implements a weighted 5-category vendor risk assessment framework designed for GCC environments operating under multiple simultaneous regulatory jurisdictions. It provides automated DPA validation, subprocessor tracking, certification monitoring, and multi-jurisdiction compliance checking.

**Script:** [Augmented_GCC_Compliance_M4_2_VendorRiskAssessment.md](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M4_2_VendorRiskAssessment.md)

**Track:** GCC Compliance Basics
**Module:** M4.2 - Enterprise Integration & Governance
**Processing Mode:** OFFLINE (No external AI/ML services required)

---

## Concepts Covered

This module implements **5 core concepts** from the augmented script:

### 1. Vendor Risk Propagation
Understanding how vendor security incidents propagate through multi-tenant GCC environments, affecting multiple business units and triggering jurisdiction-specific notification requirements.

### 2. Weighted Evaluation Matrix
5-category weighted risk assessment:
- **Security (30%):** SOC 2, ISO 27001, penetration testing, breach history
- **Privacy (25%):** GDPR compliance, DPA availability, data handling transparency
- **Compliance (20%):** Industry certifications, audit recency, regulatory violations
- **Reliability (15%):** SLA guarantees, actual uptime, support response times
- **Data Residency (10%):** Geographic controls, subprocessor transparency

### 3. Data Processing Agreements (DPAs)
Automated validation of 12 essential DPA clauses including processing scope, purpose limitation, security requirements, subprocessor approval, breach notification, and data deletion procedures.

### 4. Subprocessor Risk Management
Registry-based tracking of third-party vendors used by primary vendors, with risk inheritance analysis and approval workflows to prevent unauthorized vendor additions.

### 5. Continuous Monitoring Automation
Quarterly review scheduling, certification expiration tracking (90-day warnings), SLA compliance measurement, and incident propagation monitoring across multi-tenant environments.

---

## Learning Outcomes

After using this module, you will be able to:

1. **Implement weighted risk assessment** across 5 vendor evaluation categories
2. **Automate DPA validation** against 12 essential GDPR/DPDPA clauses
3. **Track subprocessor chains** to identify hidden third-party risks
4. **Monitor certifications** with automated expiry warnings
5. **Ensure multi-jurisdiction compliance** (GDPR, DPDPA, CCPA, SOX)
6. **Calculate ROI** for vendor management automation
7. **Identify blast radius** of vendor incidents across business units
8. **Implement continuous monitoring** with quarterly review schedules

---

## Key Features

- **5-Category Risk Assessment:** Weighted evaluation with configurable thresholds
- **Automated DPA Validation:** 12-clause checker with coverage percentage
- **Subprocessor Registry:** Track vendor dependencies and risk inheritance
- **Multi-Jurisdiction Compliance:** GDPR, DPDPA, CCPA simultaneous checking
- **Certification Monitoring:** 90-day expiry warnings for SOC 2/ISO 27001
- **ROI Calculator:** Cost analysis for automation vs manual processes
- **RESTful API:** FastAPI-based production endpoints
- **PostgreSQL Integration:** Vendor registry and assessment history
- **Comprehensive Testing:** Pytest suite with 90%+ coverage
- **Interactive Notebook:** Jupyter walkthrough with examples

---

## Prerequisites

- Python 3.9+
- pip package manager
- PostgreSQL (optional, for vendor registry persistence)
- No external API services required (OFFLINE processing)

---

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd gcc_comp_m4_v2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (optional - defaults work for basic usage)
```

### 4. (Optional) Setup PostgreSQL
```bash
# If using database persistence
createdb vendor_risk_db
# Update .env with database credentials
```

---

## Usage

### As Python Package

```python
from src.l3_m4_enterprise_integration_governance import assess_vendor
from datetime import datetime

# Vendor data
vendor_data = {
    "name": "CloudProvider Inc",
    "soc2_date": datetime(2024, 6, 1),
    "iso27001_certified": True,
    "penetration_testing": True,
    "breach_count": 0,
    "gdpr_compliant": True,
    "dpa_available": True,
    "data_deletion_automated": True,
    "sla_guarantee": 99.9,
    "actual_uptime": 99.95,
    "data_center_locations": ["US", "EU", "India"],
    "subprocessors": [
        {"name": "SubVendor A", "location": "US", "has_dpa": True}
    ]
}

# Perform assessment
result = assess_vendor(
    vendor_data=vendor_data,
    jurisdictions=["GDPR", "DPDPA", "CCPA"]
)

print(f"Risk Level: {result['risk_assessment']['risk_level']}")
print(f"Overall Score: {result['risk_assessment']['overall_score']}/100")
```

### As API Service

**Start the API server:**

**Windows PowerShell:**
```powershell
./scripts/run_api.ps1
```

**Linux/Mac:**
```bash
export PYTHONPATH=$PWD
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Test the API:**
```bash
curl -X POST "http://localhost:8000/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CloudProvider Inc",
    "soc2_date": "2024-06-01",
    "iso27001_certified": true,
    "gdpr_compliant": true,
    "dpa_available": true,
    "sla_guarantee": 99.9,
    "actual_uptime": 99.95,
    "data_center_locations": ["US", "EU", "India"],
    "jurisdictions": ["GDPR", "DPDPA"]
  }'
```

**Access interactive documentation:**
```
http://localhost:8000/docs
```

### Interactive Notebook

Launch Jupyter:
```bash
jupyter notebook notebooks/L3_M4_Enterprise_Integration_Governance.ipynb
```

---

## Project Structure

```
gcc_comp_m4_v2/
├── app.py                              # FastAPI entrypoint
├── config.py                           # Configuration management
├── requirements.txt                    # Dependencies
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
├── LICENSE                             # MIT license
├── README.md                           # This file
├── example_data.json                   # Sample JSON data
├── example_data.txt                    # Sample text data
│
├── src/                                # Source code package
│   └── l3_m4_enterprise_integration_governance/
│       └── __init__.py                 # Core business logic
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M4_Enterprise_Integration_Governance.ipynb
│
├── tests/                              # Test suite
│   └── test_m4_enterprise_integration_governance.py
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API
    └── run_tests.ps1                   # Windows: Run tests
```

---

## Testing

Run all tests:

**Windows PowerShell:**
```powershell
./scripts/run_tests.ps1
```

**Linux/Mac:**
```bash
export PYTHONPATH=$PWD
pytest tests/ -v --cov=src
```

**Run specific test:**
```bash
pytest tests/test_m4_enterprise_integration_governance.py::test_vendor_assessment -v
```

---

## API Endpoints

### POST /assess
Comprehensive vendor risk assessment with multi-category evaluation.

**Request Body:**
```json
{
  "name": "string",
  "soc2_date": "2024-01-01",
  "iso27001_certified": true,
  "gdpr_compliant": true,
  "dpa_available": true,
  "sla_guarantee": 99.9,
  "jurisdictions": ["GDPR", "DPDPA"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "risk_assessment": {
      "overall_score": 85.5,
      "risk_level": "Medium Risk (Approved with Conditions)",
      "category_scores": {...}
    },
    "dpa_validation": {...},
    "jurisdiction_compliance": {...}
  }
}
```

### POST /validate-dpa
Validate DPA against 12 essential clauses.

### POST /register-subprocessor
Register subprocessor for vendor tracking.

### POST /calculate-roi
Calculate ROI for vendor management automation.

### GET /health
Health check endpoint.

### GET /
API information and available endpoints.

---

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| ENVIRONMENT | Environment name | development | No |
| LOG_LEVEL | Logging level | INFO | No |
| TIMEOUT | Request timeout (seconds) | 30 | No |
| MAX_RETRIES | Max retry attempts | 3 | No |
| DB_HOST | PostgreSQL host | localhost | No |
| DB_PORT | PostgreSQL port | 5432 | No |
| DB_NAME | Database name | vendor_risk_db | No |
| DB_USER | Database user | postgres | No |
| DB_PASSWORD | Database password | - | No |
| QUARTERLY_REVIEW_DAYS | Days between reviews | 90 | No |
| CERTIFICATION_WARNING_DAYS | Warning days before expiry | 90 | No |
| RISK_THRESHOLD_LOW | Low risk threshold | 90 | No |
| RISK_THRESHOLD_MEDIUM | Medium risk threshold | 70 | No |
| RISK_THRESHOLD_HIGH | High risk threshold | 50 | No |
| NOTIFICATIONS_ENABLED | Enable email alerts | false | No |

**Note:** This module uses OFFLINE processing (no external AI/ML API services required)

---

## Architecture

### How It Works

```
┌─────────────────┐
│  Vendor Data    │
│  (Input)        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   VendorRiskAssessment Engine           │
│                                         │
│   ┌─────────────┐  ┌──────────────┐   │
│   │  Security   │  │   Privacy    │   │
│   │  (30%)      │  │   (25%)      │   │
│   └─────────────┘  └──────────────┘   │
│                                         │
│   ┌─────────────┐  ┌──────────────┐   │
│   │ Compliance  │  │ Reliability  │   │
│   │  (20%)      │  │   (15%)      │   │
│   └─────────────┘  └──────────────┘   │
│                                         │
│   ┌──────────────────────────┐         │
│   │  Data Residency (10%)    │         │
│   └──────────────────────────┘         │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Weighted Score Calculation            │
│   (0-100 scale)                         │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Risk Level Determination              │
│   • 90-100: Low Risk (Approved)         │
│   • 70-89: Medium (Approved w/ Conds)   │
│   • 50-69: High (Additional Controls)   │
│   • 0-49: Critical (Rejected)           │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Parallel Validations                  │
│   • DPA Clause Checking (12 clauses)    │
│   • Subprocessor Risk Inheritance       │
│   • Multi-Jurisdiction Compliance       │
│   • Certification Expiry Monitoring     │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Assessment Report                     │
│   (JSON/API Response)                   │
└─────────────────────────────────────────┘
```

### Component Interaction

1. **VendorRiskAssessment:** Core evaluation engine with weighted scoring
2. **DPAValidator:** 12-clause compliance checker
3. **SubprocessorRegistry:** Dependency tracking and risk inheritance
4. **ContinuousMonitor:** Quarterly reviews and expiry tracking
5. **Multi-Jurisdiction Checker:** GDPR/DPDPA/CCPA simultaneous validation

---

## Failure Scenarios

This module addresses **5 critical failure scenarios** identified in GCC environments:

### Failure 1: Expired Certifications Undetected
**Symptom:** SOC 2 report expires; GCC continues using vendor
**Impact:** Audit finding; potential GDPR Article 28 violation
**Prevention:** Automated expiration tracking with 90-day warning alerts

**Implementation:**
```python
monitor = ContinuousMonitor()
expiry_check = monitor.check_certification_expiry(vendor_profile)
# Returns warnings for certs expiring in < 90 days
```

### Failure 2: Subprocessor Chain Risk Blindness
**Symptom:** Vendor uses US cloud provider unknown to GCC; EU data stored in US without SCCs
**Impact:** Schrems II violation; potential €20M or 4% revenue fine
**Prevention:** Mandatory subprocessor registry with risk re-evaluation

**Implementation:**
```python
registry = SubprocessorRegistry()
risk_analysis = registry.check_risk_inheritance(vendor_name)
# Flags subprocessors lacking equivalent DPA coverage
```

### Failure 3: DPA Clause Gaps Missed During Renewal
**Symptom:** Vendor modifies DPA, removes data deletion clause; GCC signs without review
**Impact:** Cannot comply with GDPR Article 17 (Right to Erasure)
**Prevention:** Automated clause checklist flagging additions/deletions

**Implementation:**
```python
validator = DPAValidator()
dpa_result = validator.validate_dpa(dpa_text)
# Returns missing_clauses list for immediate action
```

### Failure 4: Multi-Jurisdiction Conflict
**Symptom:** Vendor is GDPR-compliant but fails India DPDPA data residency requirement
**Impact:** Cannot use vendor for India-domiciled data processing
**Prevention:** Three-layer compliance matrix validated before approval

**Implementation:**
```python
compliance = multi_jurisdiction_compliance_check(
    vendor_profile,
    jurisdictions=["GDPR", "DPDPA", "CCPA"]
)
# Returns overall_compliant: false if ANY jurisdiction fails
```

### Failure 5: Shared Services Blast Radius Underestimation
**Symptom:** Vendor breach affects 50 BUs; each responds independently creating chaos
**Impact:** Delayed incident response; inconsistent breach notifications across jurisdictions
**Prevention:** Pre-defined tenant impact maps; coordinated response playbooks

**Implementation:**
```python
# Multi-tenant aware assessment tracks which BUs use each vendor
# Incident notifications automatically identify affected jurisdictions
```

---

## Decision Card

### Vendor Assessment Pre-Approval Checklist

Before approving any vendor, ensure ALL criteria are met:

#### Risk Assessment Criteria
- ✅ **Risk score calculated** (≥50 required; <50 triggers automatic rejection)
- ✅ **Category scores reviewed** (no category below 40/100)
- ✅ **Breach history evaluated** (max 2 breaches in past 3 years)

#### DPA & Legal Requirements
- ✅ **DPA reviewed and signed** (automated clause validation passed)
- ✅ **All 12 essential clauses present** (100% coverage required)
- ✅ **Legal counsel review completed** (for contracts >$100K annually)

#### Subprocessor Management
- ✅ **Subprocessor list obtained and assessed**
- ✅ **All subprocessors have equivalent DPA coverage**
- ✅ **No unauthorized third-party vendors in chain**

#### Multi-Jurisdiction Compliance
- ✅ **Parent company requirements met** (SOX, parent jurisdiction privacy laws)
- ✅ **India operations compliant** (DPDPA, RBI data residency if applicable)
- ✅ **Client-specific mandates verified** (GDPR for EU clients, CCPA for California, HIPAA for healthcare)

#### Operational Requirements
- ✅ **SLA commitments documented** with performance baselines
- ✅ **Data residency locations confirmed** against requirements
- ✅ **Incident response procedures integrated** with GCC playbooks
- ✅ **Tenant impact analysis completed** (which BUs will use this vendor)

#### Financial & Governance
- ✅ **CFO cost-benefit approval obtained**
- ✅ **Quarterly review schedule established**
- ✅ **Certification expiry tracking configured** (90-day warnings)

### Automatic Rejection Criteria

If ANY of these apply, **REJECT** the vendor immediately:

- ❌ **Multiple security breaches** in past 3 years (≥3 breaches)
- ❌ **GDPR non-compliance** without available DPA
- ❌ **No SOC 2 report available** (or equivalent security certification)
- ❌ **DPDPA non-compliance** for India data processing
- ❌ **Critical reliability failures** (SLA <99.5% or actual uptime <99.0%)
- ❌ **Risk score below 50** (Critical Risk threshold)
- ❌ **Subprocessor chain risks** cannot be mitigated

---

## Cost & ROI Analysis

### Manual vs Automated Vendor Management

**Manual Costs (in INR lakhs):**
- 1 analyst per ~10 vendors at ₹8L annually
- 20 vendors = 2 analysts = ₹16L/year
- 50 vendors (common in GCC) = 5 analysts = ₹40L/year

**Automated System Costs (in INR lakhs):**
- Infrastructure: ₹12L/year
- Maintenance engineering (0.5 FTE): ₹4L/year
- **Total:** ₹16L/year

**ROI Calculation:**
```python
from src.l3_m4_enterprise_integration_governance import calculate_roi

roi = calculate_roi(vendor_count=50)
# Returns: {
#   "vendor_count": 50,
#   "manual_cost_lakhs": 40,
#   "automated_cost_lakhs": 16,
#   "annual_savings_lakhs": 24,
#   "roi_percentage": 150.0,
#   "breakeven_vendors": 20
# }
```

**Breakeven Point:** 20 vendors

---

## Integration with Other Modules

This module integrates with:

- **M4.1 Model Cards:** Auto-populates vendor dependencies section from registry
- **M3.2 Audit Logging:** Cross-references vendor data access against authorization logs
- **M2.1 Secrets Management:** Ensures vendor API keys stored in vault infrastructure
- **Deployment Pipeline:** Automated weekly vendor status checks via CI/CD

---

## Technology Stack

- **Language:** Python 3.9+
- **API Framework:** FastAPI + Uvicorn
- **Data Processing:** pandas, requests
- **Excel Processing:** openpyxl (for vendor reports)
- **PDF Generation:** reportlab (for assessment reports)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Testing:** pytest with asyncio support
- **Monitoring:** Grafana for risk dashboard visualization (optional)
- **Notifications:** SMTP/Slack for automated alerting (optional)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `pytest tests/ -v --cov=src`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Submit a pull request

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Support

For issues and questions:
- **GitHub Issues:** Open an issue on GitHub
- **Documentation:** Refer to the [augmented script](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M4_2_VendorRiskAssessment.md)
- **Interactive Tutorial:** Check the Jupyter notebook for examples

---

## Disclaimer

This assessment framework provides risk scoring methodology, **not legal counsel**. All DPA contracts require attorney review. Vendor risk assessment complements but does not replace formal legal and procurement processes. GCCs must obtain parent company approval before finalizing vendor relationships.

---

## Version

**1.0.0** - Initial release based on augmented script (2024)

---

## References

- [Augmented Script](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/blob/main/Augmented_GCC_Compliance_M4_2_VendorRiskAssessment.md)
- [GDPR Article 28](https://gdpr-info.eu/art-28-gdpr/) - Processor requirements
- [India DPDPA](https://www.meity.gov.in/writereaddata/files/Digital%20Personal%20Data%20Protection%20Act%202023.pdf)
- [Schrems II Decision](https://curia.europa.eu/juris/document/document.jsf?docid=228677)
- [CCPA Regulations](https://oag.ca.gov/privacy/ccpa)
