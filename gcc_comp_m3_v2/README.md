# L3 M3.2: Automated Compliance Testing

## Overview

Automated compliance testing using **Open Policy Agent (OPA)** and **Rego** policy-as-code for RAG systems. This module transforms compliance from documentation-based to executable, testable policies that run in CI/CD pipelines.

**Key Concept:** Prevention over detection - catch compliance violations *before* they reach production, not after 2 AM.

## What Problem Does This Solve?

Traditional compliance approach:
- Manual reviews before deployment
- Violations discovered in production
- Audit preparation takes 8+ hours
- No regression testing for controls

**Policy-as-Code Solution:**
- Automated validation in CI/CD (2-5 minutes)
- 95%+ violations caught before deployment
- Audit evidence auto-generated
- Continuous control verification

## Prerequisites

- Python 3.10+
- Open Policy Agent (OPA) binary - [Download](https://www.openpolicyagent.org/docs/latest/)
- Optional: Presidio for enhanced PII detection
- Completed: GCC Compliance M1 (Regulatory Foundations) and M2 (Core Controls)

## Technology Stack

**Core Components:**
- **OPA (Open Policy Agent)** - Policy engine with Rego language
- **Conftest** - Configuration testing tool (optional)
- **Python** - Test harness and API wrapper
- **FastAPI** - HTTP API for compliance validation
- **Presidio** - Optional enhanced PII detection

**Cost Estimate:**
- Small GCC: ~$50/month (infrastructure only)
- Medium GCC: ~$300/month
- Large GCC: ~$1,300/month
- OPA/Presidio: Free (open-source)

## Installation & Setup

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd gcc_comp_m3_v2
pip install -r requirements.txt
```

### 2. Install OPA Binary (Optional but Recommended)

**Linux/MacOS:**
```bash
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/
```

**Windows:**
```powershell
# Download from https://openpolicyagent.org/downloads/latest/opa_windows_amd64.exe
# Rename to opa.exe and add to PATH
```

### 3. Install Presidio (Optional)

```bash
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

**Key Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `OPA_ENABLED` | Enable OPA policy engine | `false` |
| `OPA_BINARY_PATH` | Path to OPA binary | `opa` |
| `OPA_POLICY_PATH` | Path to `.rego` policy files | `./policies` |
| `PRESIDIO_ENABLED` | Enable Presidio PII detection | `false` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `TEST_COVERAGE_THRESHOLD` | Minimum test coverage | `95.0` |

## Usage

### 1. API Mode (FastAPI)

**Start the API server:**

```powershell
# Windows PowerShell
.\scripts\run_api.ps1
```

```bash
# Or directly:
uvicorn app:app --reload
```

**Access API documentation:**
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/

**API Endpoints:**
- `POST /pii/check` - Check if text contains PII
- `POST /pii/redaction` - Validate redaction quality
- `POST /compliance/check` - Full compliance validation
- `POST /policy/evaluate` - Evaluate OPA policy
- `POST /tests/run` - Execute compliance test suite
- `GET /health` - Detailed health check

### 2. Python Package Mode

```python
from src.l3_m3_monitoring_reporting import (
    check_compliance,
    contains_pii,
    redaction_quality_sufficient,
    run_compliance_tests
)

# Check for PII
has_pii = contains_pii("Customer SSN: 123-45-6789")
print(f"Has PII: {has_pii}")  # True

# Validate compliance
result = check_compliance(
    operation='embed',
    text='Financial data without PII'
)
print(f"Allowed: {result.allowed}")  # True
print(f"Violations: {result.violations}")  # []

# Run full test suite
test_results = run_compliance_tests()
print(f"Pass rate: {test_results['pass_rate']:.1f}%")
```

### 3. Jupyter Notebook Mode

```bash
jupyter notebook notebooks/L3_M3_Monitoring_Reporting.ipynb
```

Interactive learning experience with:
- Policy-as-code concepts
- PII detection demos
- OPA/Rego policy examples
- Test pyramid implementation
- CI/CD integration patterns

### 4. Running Tests

**Execute compliance test suite:**

```powershell
# Windows PowerShell
.\scripts\run_tests.ps1
```

```bash
# Or directly:
pytest tests/ -v --cov=src/l3_m3_monitoring_reporting
```

**Test Pyramid Coverage:**
- **70% Unit Tests** - PII detection patterns (15-20 tests)
- **20% Integration Tests** - Policy integration (10-15 tests)
- **10% End-to-End Tests** - Full workflow (5-10 tests)
- **Target:** 55-77 total tests per deployment

## How It Works

### Architecture

```
┌─────────────────┐
│   RAG System    │
│  (Your App)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Compliance API  │
│   (FastAPI)     │
└────────┬────────┘
         │
         v
┌─────────────────┐      ┌──────────────┐
│ Policy Engine   │◄────►│ Presidio PII │
│     (OPA)       │      │  (Optional)  │
└────────┬────────┘      └──────────────┘
         │
         v
┌─────────────────┐
│  Rego Policies  │
│  (.rego files)  │
└─────────────────┘
```

### PII Detection Logic

**Regex-based patterns (default):**
- SSN: `\b\d{3}-\d{2}-\d{4}\b`
- Email: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
- Credit Card: `\b(?:\d{4}[-\s]?){3}\d{4}\b`
- Phone: `\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b`

**Policy Logic (OPA Rego):**
```rego
package ragcompliance.pii

# Default deny principle
default allow_embedding = false

# Allow if no PII detected
allow_embedding {
    not contains_pii(input.text)
}

# Allow if PII properly redacted
allow_embedding {
    contains_pii(input.text)
    redaction_quality_sufficient(input.text)
}

# Deny and generate violation message
violation[msg] {
    contains_pii(input.text)
    not redaction_quality_sufficient(input.text)
    msg := sprintf("PII detected without proper redaction: %v", [input.text])
}
```

## Compliance Standards Supported

- **GDPR Article 17** - Right to be forgotten (PII redaction)
- **DPDPA Section 12** - Data protection and minimization
- **SOX** - 7-year retention for financial records
- **SOC 2** - Continuous monitoring and audit evidence
- **ISO 27001** - Information security controls

## Decision Card

**When to Use Automated Compliance Testing:**

### ✅ Use When:
- **High-stakes compliance requirements** - Financial services, healthcare, government sectors requiring SOC 2, ISO 27001, GDPR
- **Frequent deployments** - CI/CD pipelines with multiple releases per week
- **Audit requirements** - Need automated evidence generation and control persistence verification
- **Repeatable testing needed** - Regression prevention across 55-77 automated tests
- **Documentation-heavy compliance** - Converting manual checklists to executable policies

### ❌ Don't Use When:
- **Prototype/MVP stage** - Pre-product-market fit, compliance premature
- **Low-risk applications** - Internal tools without PII, no regulatory requirements
- **Team lacks policy expertise** - No one can write/maintain Rego policies
- **One-time audits** - Manual review more efficient than automation setup
- **Simple rules suffice** - Basic linting or static analysis meets needs

### 🔀 Alternative Approaches:
- **Instead of OPA:** Kyverno (Kubernetes-native), Cloud Custodian (cloud resources), custom Python validators
- **Instead of Conftest:** OPA eval command, Gatekeeper (K8s admission controller)
- **Instead of GitHub Actions:** GitLab CI, Jenkins, CircleCI

### ⚖️ Trade-offs:
- **Learning curve** - Rego language requires 2-4 weeks proficiency
- **Initial setup time** - 1-2 sprints for first policy suite vs. ongoing manual review time
- **Maintenance overhead** - Policies need updates as regulations change
- **95% catch rate** - Tests catch ~95% of violations, not 100%; still need M3.1 dashboards and annual audits

## Common Failures & Fixes

| Failure Scenario | Root Cause | Fix | Prevention |
|-----------------|------------|-----|------------|
| **1. Tests pass in CI but fail audit** | Incomplete test coverage; policies don't match actual regulations | Cross-reference policies with regulatory text; engage compliance experts | Require legal/compliance sign-off on policy changes; >95% coverage threshold |
| **2. PII slips through detection** | Regex patterns miss edge cases (international formats, typos) | Enhance Presidio integration; add negative test cases for edge cases | Maintain pattern library; log undetected PII from production incidents |
| **3. False positives block valid data** | Overly aggressive patterns (e.g., dates mistaken for SSN) | Add context-aware checks; whitelist known safe patterns | Review blocked operations weekly; tune threshold |
| **4. CI tests take >10 minutes** | Running full test suite on every commit | Parallelize tests; run subset on PR, full suite on merge | Cache OPA binary; optimize test data size |
| **5. Policies become unmaintainable** | Monolithic .rego files; no modular structure | Split into packages by compliance area (pii, retention, access) | Enforce 200-line file limit; require docs per policy |
| **6. OPA binary not found** | OPA not installed or not in PATH | Install OPA binary, set `OPA_BINARY_PATH` in .env | Add OPA installation to onboarding docs; CI/CD setup script |
| **7. Presidio import errors** | Missing spacy model or presidio packages | Run: `pip install presidio-analyzer && python -m spacy download en_core_web_lg` | Add to requirements.txt and setup script |
| **8. Tests fail with "Service unavailable"** | OPA_ENABLED=false but tests expect OPA | Set `OPA_ENABLED=true` after installing OPA binary | Graceful degradation to regex-only mode; clear error messages |

## Example Use Case: Preventing PII Leakage

**Scenario:** Preventing Social Security Numbers from being embedded in vector database

**Traditional Approach:**
```python
# Manual review before deployment - time-consuming, error-prone
text = "Customer SSN: 123-45-6789"
embeddings = embed(text)  # ⚠️ PII leaked!
```

**Automated Compliance Approach:**
```python
from src.l3_m3_monitoring_reporting import check_compliance

text = "Customer SSN: 123-45-6789"

# Check compliance before embedding
result = check_compliance(operation='embed', text=text)

if result.allowed:
    embeddings = embed(text)
else:
    print(f"❌ Blocked: {result.violations}")
    # Output: ❌ Blocked: ['Found ssn: 1 instance(s) - GDPR Article 17, DPDPA Section 12 violation']

    # Redact PII and retry
    redacted_text = "Customer SSN: [REDACTED]"
    result = check_compliance(operation='embed', text=redacted_text)
    if result.allowed:
        embeddings = embed(redacted_text)  # ✓ Safe to embed
```

## CI/CD Integration

**GitHub Actions Example:**

```yaml
name: Compliance Testing

on: [push, pull_request]

jobs:
  compliance-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install OPA
        run: |
          curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
          chmod +x opa
          sudo mv opa /usr/local/bin/

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run compliance tests
        run: |
          pytest tests/ --cov=src/l3_m3_monitoring_reporting --cov-fail-under=95

      - name: Block on violations
        if: failure()
        run: exit 1
```

## Metrics & Impact

**Key Performance Indicators:**
- **Violation Prevention:** 95%+ regressions caught in CI
- **Audit Preparation:** 8 hours → 30 minutes (16x improvement)
- **Test Execution:** 2-5 minutes per CI run
- **Control Coverage:** 99%+ PII detection, 100% unauthorized access blocking
- **Audit Logging:** 99.5%+ operation logging

## Learning Outcomes

By completing this module, you will:

1. **Implement policy-as-code** with OPA/Rego for compliance validation
2. **Build automated test suites** following the test pyramid (70/20/10 split)
3. **Integrate testing into CI/CD** with deployment gates blocking violations
4. **Create regression tests** ensuring control persistence across releases
5. **Generate automated audit evidence** reducing manual audit preparation time
6. **Write and test Rego policies** for RAG systems covering PII, access, audit, retention

## Limitations & Reality Check

- Tests catch **~95% of violations**, not 100%
- Still requires:
  - M3.1 dashboards for runtime detection
  - Annual third-party audits for independent verification
  - Incident response for the 5% that slip through
- Rego learning curve: 2-4 weeks for proficiency
- Initial setup: 1-2 sprints for first policy suite
- Ongoing maintenance as regulations evolve

## Architecture Decisions

**Why OPA over custom validation?**
- Industry-standard policy engine
- Rego language designed for declarative policies
- Large ecosystem (Kubernetes, cloud providers)
- Better than custom Python validators (hard to audit, no standard format)

**Why Presidio as optional enhancement?**
- Microsoft-backed, production-ready
- Supports 15+ entity types out-of-box
- ML-based detection for edge cases
- Fallback to regex if unavailable (no hard dependency)

**Why regex-based by default?**
- Zero external dependencies
- Fast execution (microseconds)
- Transparent pattern matching
- Easy to audit and debug

## Project Structure

```
gcc_comp_m3_v2/
├── app.py                              # FastAPI entrypoint
├── config.py                           # Environment & client management
├── requirements.txt                    # Pinned dependencies
├── .env.example                        # Environment template
├── .gitignore                          # Python defaults
├── LICENSE                             # MIT License
├── README.md                           # This file
├── example_data.json                   # Test case data
├── example_data.txt                    # Sample text data
│
├── src/                                # Source code package
│   └── l3_m3_monitoring_reporting/          # Python package
│       └── __init__.py                 # Core business logic
│
├── notebooks/                          # Jupyter notebooks
│   └── L3_M3_Monitoring_Reporting.ipynb     # Interactive walkthrough
│
├── tests/                              # Test suite
│   └── test_m3_monitoring_reporting.py      # Pytest-compatible tests
│
├── configs/                            # Configuration files
│   └── example.json                    # Sample config
│
└── scripts/                            # Automation scripts
    ├── run_api.ps1                     # Windows: Start API
    └── run_tests.ps1                   # Windows: Run tests
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Run tests: `pytest tests/`
4. Ensure 95%+ coverage: `pytest --cov=src --cov-fail-under=95`
5. Commit with clear messages
6. Push and create a pull request

## Resources

- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Rego Playground](https://play.openpolicyagent.org/)
- [Presidio Documentation](https://microsoft.github.io/presidio/)
- [GCC Compliance M1: Regulatory Foundations](../M1/)
- [GCC Compliance M2: Core Controls](../M2/)
- [GCC Compliance M3.1: Monitoring Dashboards](../M3.1/)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues or questions:
- Open an issue in the repository
- Refer to `/docs` endpoint for API documentation
- Check example_data.json for sample test cases

---

**Next Steps:**
- Complete M3.3: Incident Response
- Integrate with existing M3.1 monitoring dashboards
- Set up CI/CD pipeline with compliance gates
- Schedule first compliance test automation review
