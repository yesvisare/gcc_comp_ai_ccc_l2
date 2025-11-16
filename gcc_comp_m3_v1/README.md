# L3 M3.1: Compliance Monitoring Dashboards

Production-grade compliance monitoring system for RAG deployments in Global Capability Centers (GCC). Provides real-time visibility into compliance posture across 50+ business units with multi-tenant metrics isolation, stakeholder-specific dashboards, and automated SOC2 evidence generation.

**Part of:** TechVoyageHub L3 Production RAG Engineering Track
**Prerequisites:**
- Generic CCC M1-M4 (RAG MVP fundamentals)
- GCC Compliance M1.1-M1.2 (Why Compliance Matters, Compliance Frameworks)
- GCC Compliance M2.1-M2.2 (Security Controls, Incident Response)
- Understanding of Prometheus, Grafana basics

**Services:** PROMETHEUS (metrics collection) + GRAFANA (visualization) + OPA (policy validation)

## What You'll Build

Transform compliance from a quarterly checkbox exercise into continuous, real-time visibility that prevents violations before they become incidents. This system gives you instant answers to critical questions:

- âœ" Are we leaking PII?
- âœ" Are access controls working?
- âœ" Is our audit trail complete?
- âœ" Are we ready for the SOX 404 audit next month?

**Key Capabilities:**

1. **Continuous Compliance Metrics Collection** - Instrument every component of your RAG pipeline (ingestion, vector storage, retrieval, generation) to emit compliance-specific metrics
2. **Real-Time Compliance KPI Visualization** - Grafana dashboards showing 6 critical KPIs with 15-second refresh rates
3. **Stakeholder-Specific Views** - CFO sees cost and audit readiness, CTO sees technical health, Compliance Officer sees regulatory adherence
4. **Automated SOC2 Evidence Generation** - One-click timestamped reports proving control effectiveness over 90-day periods

**Success Criteria:**

- Real-time visibility into 6 compliance KPIs across all business units
- Automated alerts triggered within 60 seconds of threshold violations
- Stakeholder dashboards tailored to CFO, CTO, and Compliance Officer needs
- SOC2 audit evidence exportable in auditor-expected formats
- Multi-tenant metrics isolation (per business unit view)
- 13-month data retention for SOX compliance requirements

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RAG Pipeline Components                           │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌────────────┐            │
│  │Ingestion │→ │Vector Store│→ │Retrieval │→ │Generation  │            │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └──────┬─────┘            │
│       │              │              │               │                   │
│       ↓              ↓              ↓               ↓                   │
│  ┌────────────────────────────────────────────────────────┐            │
│  │         Compliance Metrics Collection                   │            │
│  │  • PII Detection Rate                                  │            │
│  │  • Access Control Violations                           │            │
│  │  • Audit Trail Completeness                           │            │
│  └──────────────────┬─────────────────────────────────────┘            │
└─────────────────────┼──────────────────────────────────────────────────┘
                      ↓
          ┌───────────────────────┐
          │   Prometheus          │  ← Metrics time-series database
          │   (13-month retention)│     (SOX requirement)
          └───────────┬───────────┘
                      ↓
          ┌───────────────────────┐
          │   KPI Calculator      │  ← Compute 6 compliance KPIs
          │                       │
          │  1. Audit Completeness│     Target: >99%
          │  2. PII Precision     │     Target: >95%
          │  3. PII Recall        │     Target: >99%
          │  4. Access Violations │     Target: <0.1%
          │  5. Encryption        │     Target: 100%
          │  6. Cert Expiry       │     Warning: 30 days
          └───────────┬───────────┘
                      ↓
          ┌───────────────────────────────────────────┐
          │         Grafana Dashboards                │
          ├───────────┬───────────┬───────────────────┤
          │ CFO View  │ CTO View  │ Compliance Officer│
          │           │           │       View        │
          │• Audit    │• Encryption│• PII Detection   │
          │  Readiness│  Coverage │  Accuracy        │
          │• Cost     │• Tech      │• Violation       │
          │  Tracking │  Health    │  Trends          │
          └───────────┴───────────┴───────────────────┘
                      ↓
          ┌───────────────────────┐
          │   Alert Manager       │
          │                       │
          │  Critical → PagerDuty │
          │  Warning  → Slack     │
          │  Info     → Email     │
          └───────────────────────┘
```

## Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd gcc_comp_m3_v1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and configure services:
# - Set PROMETHEUS_ENABLED=true if you have Prometheus running
# - Set GRAFANA_ENABLED=true if you have Grafana running
# - Set GRAFANA_API_KEY for programmatic dashboard creation
```

### 4. Run Tests
```bash
# Windows PowerShell
.\scripts\run_tests.ps1

# Or manually
$env:PYTHONPATH=$PWD; pytest -v tests/
```

### 5. Start API
```bash
# Windows PowerShell
.\scripts\run_api.ps1

# Or manually
$env:PYTHONPATH=$PWD; uvicorn app:app --reload
```

API will be available at:
- http://localhost:8000 (health check)
- http://localhost:8000/docs (interactive API documentation)

### 6. Explore Notebook
```bash
jupyter lab notebooks/L3_M3_Monitoring_Reporting.ipynb
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROMETHEUS_ENABLED` | No | `false` | Enable Prometheus metrics collection |
| `PROMETHEUS_PUSHGATEWAY_URL` | If enabled | `http://localhost:9091` | Prometheus pushgateway endpoint |
| `PROMETHEUS_RETENTION_DAYS` | No | `395` | Metrics retention (13 months for SOX) |
| `GRAFANA_ENABLED` | No | `false` | Enable Grafana dashboard integration |
| `GRAFANA_URL` | If enabled | `http://localhost:3000` | Grafana instance URL |
| `GRAFANA_API_KEY` | If enabled | - | API key for dashboard creation |
| `OPA_ENABLED` | No | `false` | Enable OPA policy validation |
| `OPA_URL` | If enabled | `http://localhost:8181` | OPA server URL |
| `ALERTMANAGER_ENABLED` | No | `false` | Enable alert management |
| `ALERTMANAGER_URL` | If enabled | `http://localhost:9093` | AlertManager URL |
| `PAGERDUTY_API_KEY` | If enabled | - | PagerDuty integration key |
| `SLACK_WEBHOOK_URL` | If enabled | - | Slack webhook for alerts |
| `THRESHOLD_AUDIT_COMPLETENESS` | No | `99.0` | Audit trail completeness threshold (%) |
| `THRESHOLD_PII_PRECISION` | No | `95.0` | PII detection precision threshold (%) |
| `THRESHOLD_PII_RECALL` | No | `99.0` | PII detection recall threshold (%) |
| `THRESHOLD_ACCESS_VIOLATIONS` | No | `0.1` | Access control violation threshold (%) |
| `THRESHOLD_ENCRYPTION` | No | `100.0` | Encryption coverage threshold (%) |
| `THRESHOLD_CERT_EXPIRY` | No | `30` | Certificate expiry warning (days) |
| `OFFLINE` | No | `false` | Run in offline mode (notebook/testing) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

## API Endpoints

### Health & Configuration

**GET /**
- Health check endpoint
- Returns service status and enabled features

**GET /config**
- Get current configuration and thresholds
- Returns all environment settings

**GET /health**
- Detailed health check with service availability

### Metrics Collection

**POST /metrics/collect**
- Collect compliance metrics from RAG components
- Request body:
  ```json
  {
    "tenant_id": "business_unit_001",
    "documents": [...],  // Optional: for PII metrics
    "access_logs": [...], // Optional: for access control metrics
    "events": [...]      // Optional: for audit trail metrics
  }
  ```

### KPI Calculation

**GET /kpis/calculate**
- Calculate all 6 compliance KPIs from collected metrics
- Query params: `tenant_id` (optional, filter by tenant)
- Returns: KPI values, overall compliance score, compliance status

### Dashboard Generation

**POST /dashboards/generate**
- Generate Grafana dashboard configuration
- Request body:
  ```json
  {
    "stakeholder": "cfo"  // or "cto" or "compliance_officer"
  }
  ```
- Returns: Dashboard JSON config (Grafana-compatible)

### Evidence Export

**POST /evidence/export**
- Export SOC2 compliance evidence for audits
- Request body:
  ```json
  {
    "time_range_days": 90,  // Default: 90 days
    "format": "json"         // "json" or "csv"
  }
  ```
- Returns: SOC2 evidence report with control mappings

### Alert Evaluation

**GET /alerts/evaluate**
- Evaluate current KPIs and return triggered alerts
- Returns: List of alerts with severity and notification channels

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| **"Prometheus connection failed"** | Prometheus not running or wrong URL | Check PROMETHEUS_PUSHGATEWAY_URL, ensure Prometheus is running at specified endpoint |
| **"Grafana API authentication failed"** | Invalid or missing API key | Generate new API key in Grafana (Settings → API Keys) with Editor role |
| **"Metrics buffer full"** | Metrics not flushed to Prometheus | Call `/metrics/collect` endpoint to trigger flush, or enable PROMETHEUS_ENABLED |
| **"KPI threshold violation alert storm"** | Thresholds too strict for deployment | Adjust THRESHOLD_* environment variables to match your compliance requirements |
| **"Dashboard creation failed"** | Insufficient Grafana permissions | Ensure API key has Editor or Admin role for dashboard creation |
| **"OPA policy evaluation timeout"** | OPA server not responding | Check OPA_URL, verify OPA is running with `curl http://localhost:8181/health` |
| **"Multi-tenant metrics leakage"** | Missing tenant_id labels | Ensure all metric collection calls include valid tenant_id parameter |
| **"SOC2 evidence export incomplete"** | Insufficient data retention | Check PROMETHEUS_RETENTION_DAYS is ≥395 days (13 months for SOX) |
| **"Certificate expiry alerts false positive"** | Clock skew between systems | Sync system clocks with NTP, verify THRESHOLD_CERT_EXPIRY setting |
| **"Access control violation spike"** | Recent RBAC policy changes | Review recent authorization policy updates in OPA, check for policy bugs |

## Decision Card

### When to Use This Module

âœ" **Multi-tenant GCC deployments** - You're supporting 50+ business units with isolated compliance requirements
âœ" **Regulatory compliance obligations** - Subject to SOX 404, GDPR, DPDPA, CCPA, or SOC2 audits
âœ" **Real-time compliance visibility needed** - Can't wait 3 days for manual compliance reports
âœ" **Automated evidence generation** - Auditors require timestamped proof of control effectiveness
âœ" **Stakeholder-specific reporting** - CFO, CTO, and Compliance Officer need different views of same data
âœ" **Proactive violation prevention** - Want to catch issues within 60 seconds, not after quarterly review

### When NOT to Use This Module

âŒ **Single-tenant, low-risk deployments** - Compliance requirements are minimal or non-existent
âŒ **No regulatory obligations** - Internal-only system with no audit requirements
âŒ**Manual compliance processes are sufficient** - Quarterly reviews meet your needs
âŒ **No dedicated compliance team** - No stakeholders who need compliance dashboards
âŒ **Resource-constrained environments** - Can't run Prometheus/Grafana infrastructure
âŒ **Ephemeral/prototype systems** - Short-lived deployments that don't need compliance tracking

### Trade-offs

**Infrastructure Complexity:**
- Requires Prometheus (metrics storage), Grafana (visualization), and optionally OPA (policy)
- 13-month retention requires ~10-50GB storage per 50 tenants (depends on metric cardinality)
- Adds 3-5 additional services to operational stack

**Performance Impact:**
- Metrics collection adds 5-10ms latency to RAG pipeline operations
- Prometheus scraping occurs every 15 seconds (configurable)
- Dashboard queries can impact Prometheus performance if poorly written

**Cost:**
- Managed Prometheus: ~$50-200/month for 50 tenants (depends on provider)
- Managed Grafana: ~$50-100/month for 10 concurrent users
- PagerDuty integration: $25-50/user/month for on-call alerting
- Total estimated: $150-400/month additional infrastructure cost

**Latency:**
- Metrics propagation delay: 15-30 seconds from event to dashboard visibility
- Alert triggering: 30-60 seconds from threshold violation to notification
- Dashboard refresh: 15 seconds (configurable, balance freshness vs. query load)

**Maintenance:**
- Prometheus retention management: cleanup jobs, storage monitoring
- Grafana dashboard version control: track changes, rollback broken dashboards
- Alert tuning: ongoing adjustment of thresholds to reduce false positives
- OPA policy updates: keep compliance rules in sync with regulatory changes

## Six Compliance KPIs Explained

### 1. Audit Trail Completeness (Target: >99%)
- **What:** Percentage of compliance events successfully logged to audit trail
- **Why it matters:** SOX 404, SOC2 CC7.2 require complete audit logs for all security events
- **How it's calculated:** `(events_logged / total_events) * 100`
- **Alert threshold:** <99% triggers critical alert to PagerDuty

### 2. PII Detection Precision (Target: >95%)
- **What:** Percentage of PII detection alerts that are true positives (not false alarms)
- **Why it matters:** GDPR, CCPA require accurate PII identification; too many false positives reduce trust
- **How it's calculated:** `(true_positive_pii / (true_positive_pii + false_positive_pii)) * 100`
- **Alert threshold:** <95% triggers warning to Slack (indicates detection model needs retraining)

### 3. PII Detection Recall (Target: >99%)
- **What:** Percentage of actual PII items successfully detected (not missed)
- **Why it matters:** Missing PII = data breach risk; DPDPA Section 8 penalties for undetected PII leakage
- **How it's calculated:** `(true_positive_pii / (true_positive_pii + false_negative_pii)) * 100`
- **Alert threshold:** <99% triggers critical alert (data protection risk)

### 4. Access Control Violations (Target: <0.1%)
- **What:** Percentage of access attempts that violated authorization policies
- **Why it matters:** SOC2 CC6.1 requires effective logical access controls; violations indicate RBAC bugs
- **How it's calculated:** `(unauthorized_attempts / total_attempts) * 100`
- **Alert threshold:** >0.1% triggers critical alert (potential security breach)

### 5. Encryption Coverage (Target: 100%)
- **What:** Percentage of data at rest and in transit encrypted per policy
- **Why it matters:** GDPR Article 32, SOC2 CC6.6 require encryption of sensitive data
- **How it's calculated:** `(encrypted_records / total_records) * 100`
- **Alert threshold:** <100% triggers critical alert immediately

### 6. Certificate Expiry (Target: >30 days remaining)
- **What:** Days remaining until TLS certificate expiration
- **Why it matters:** Expired certs break encryption, cause outages, fail SOC2 audits
- **How it's calculated:** `(cert_expiry_date - current_date).days`
- **Alert threshold:** <30 days triggers warning, <7 days triggers critical

## SOC2 Trust Service Criteria Mapping

This module provides evidence for the following SOC2 controls:

| Control | Name | Evidence Provided |
|---------|------|------------------|
| **CC6.1** | Logical Access Controls | Access control violation rate <0.1%, RBAC policy enforcement logs |
| **CC6.6** | Encryption | 100% encryption coverage metrics, key rotation logs |
| **CC7.2** | System Monitoring | Real-time dashboards, 99%+ audit trail completeness |
| **CC7.3** | Security Event Evaluation | Automated alert evaluation, threshold violation detection |
| **CC7.4** | Security Incident Response | PagerDuty integration, incident escalation logs |

## Troubleshooting

### Services Disabled Mode

The module will run without external service integration if services are not enabled in `.env`. The `config.py` file will skip client initialization, and API endpoints will return informative responses indicating service availability. This is the default behavior and is useful for:

- Local development without infrastructure dependencies
- Testing in CI/CD pipelines
- Exploring the API structure before deploying infrastructure

**To enable services:**
1. Install and start Prometheus/Grafana/OPA locally (or use managed services)
2. Update `.env` with connection details and API keys
3. Set `PROMETHEUS_ENABLED=true`, `GRAFANA_ENABLED=true`, etc.
4. Restart the API server

### Import Errors

If you see `ModuleNotFoundError: No module named 'src.l3_m3_monitoring_reporting'`, ensure:

```bash
# Windows PowerShell
$env:PYTHONPATH = $PWD

# Linux/Mac
export PYTHONPATH=$(pwd)
```

This is automatically handled by the PowerShell scripts in `scripts/`.

### Tests Failing

Run tests with verbose output to identify failures:

```bash
pytest -v tests/
```

Common test failures:
- **Import errors:** Set PYTHONPATH (see above)
- **Service connection errors:** Tests should run in offline mode; check `OFFLINE=true` in environment
- **Assertion failures:** Check if KPI thresholds in `config.py` match test expectations

### Dashboard Not Appearing in Grafana

1. **Check Grafana API key permissions:** Must have Editor or Admin role
2. **Verify API endpoint response:** Call `POST /dashboards/generate` and check JSON structure
3. **Manual import:** Copy JSON from API response, paste into Grafana → Import Dashboard
4. **Check Grafana logs:** `docker logs <grafana-container>` for import errors

### Metrics Not Appearing in Prometheus

1. **Check pushgateway connectivity:** `curl http://localhost:9091/metrics`
2. **Verify metric naming:** Prometheus metric names must match regex `[a-zA-Z_:][a-zA-Z0-9_:]*`
3. **Check Prometheus scrape config:** Ensure pushgateway is in `scrape_configs`
4. **Query Prometheus directly:** `http://localhost:9090/graph` to verify metrics exist

## Next Module

**GCC Compliance M3.2: Automated Compliance Testing** - Learn to automate compliance validation with continuous testing, policy-as-code enforcement, and regression prevention for regulatory requirements.

## Learning Outcomes

After completing this module, you will:

1. **Define compliance KPIs for RAG systems** - Understand which metrics matter for SOX, GDPR, SOC2 compliance
2. **Implement automated policy checks with OPA** - Write Rego policies that validate compliance rules in real-time
3. **Build real-time Grafana dashboards** - Create stakeholder-specific dashboards with color-coded thresholds
4. **Configure alerting for compliance violations** - Set up PagerDuty/Slack integration with severity-based routing
5. **Map RAG controls to SOC2 Trust Service Criteria** - Document evidence for CC6.1, CC7.2, CC6.6 controls
6. **Generate automated evidence for audits** - Export timestamped compliance reports in auditor-expected formats

## Project Structure

```
gcc_comp_m3_v1/
â"œâ"€â"€ app.py                                  # FastAPI entrypoint
â"œâ"€â"€ config.py                               # Environment & client management
â"œâ"€â"€ requirements.txt                        # Pinned dependencies
â"œâ"€â"€ .env.example                            # Environment variable template
â"œâ"€â"€ .gitignore                              # Python defaults
â"œâ"€â"€ LICENSE                                 # MIT License
â"œâ"€â"€ README.md                               # This file
â"œâ"€â"€ example_data.json                       # Sample compliance metrics
â"‚
â"œâ"€â"€ src/                                    # Source code package
â"‚   â""â"€â"€ l3_m3_monitoring_reporting/        # Python package
â"‚       â""â"€â"€ __init__.py                     # Core business logic
â"‚
â"œâ"€â"€ notebooks/                              # Jupyter notebooks
â"‚   â""â"€â"€ L3_M3_Monitoring_Reporting.ipynb   # Interactive walkthrough
â"‚
â"œâ"€â"€ tests/                                  # Test suite
â"‚   â""â"€â"€ test_m3_monitoring_reporting.py   # Pytest-compatible tests
â"‚
â"œâ"€â"€ configs/                                # Configuration files
â"‚   â""â"€â"€ example.json                        # Sample dashboard config
â"‚
â""â"€â"€ scripts/                                # Automation scripts
    â"œâ"€â"€ run_api.ps1                         # Windows: Start API
    â""â"€â"€ run_tests.ps1                       # Windows: Run tests
```

## Contributing

This module is part of the TechVoyageHub L3 Production RAG Engineering track. Contributions should:

- Maintain production-grade code quality (type hints, docstrings, tests)
- Follow the established patterns for metrics collection and KPI calculation
- Include tests for all new functionality (target: >90% coverage)
- Update documentation for any new environment variables or endpoints
- Preserve multi-tenant isolation and security controls

## License

MIT License - see LICENSE file for details.

## Support

For issues, questions, or contributions:
- GitHub Issues: [Report issues](https://github.com/yesvisare/gcc_comp_ai_ccc_l2/issues)
- Documentation: [TechVoyageHub L3 Track](https://techvoyagehub.com/tracks/l3-production-rag)
