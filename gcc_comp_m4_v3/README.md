# L3 M4.3: Change Management & Compliance

A GCC-grade change management system that handles 3 change types (Standard, Normal, Emergency), routes approvals to the right stakeholders, verifies compliance impact before implementation, and maintains an immutable audit trail for 7+ years.

**Part of:** TechVoyageHub L3 Production RAG Engineering Track
**Prerequisites:** Generic CCC M1-M4, GCC Compliance M1.1-M4.2
**SERVICE:** None (Internal governance tool - no external APIs)

## What You'll Build

A production-ready change management platform that transforms RAG deployments from 'cowboy coding' to 'audit-ready governance.' This system prevents compliance disasters like the 3 AM scenario where an unapproved embedding model change resulted in ₹2.5 crore SOX 404 fines and executive terminations.

**Key Capabilities:**
- **Classify changes automatically** - Is this embedding model update Standard, Normal, or Emergency?
- **Route approvals intelligently** - Send to manager, Change Advisory Board (CAB), or CISO based on risk
- **Verify compliance before deploy** - Check SOX, GDPR, DPDPA impact automatically
- **Execute rollback in <15 minutes** - Auto-rollback if compliance tests fail post-deploy
- **Generate audit-ready reports** - Show auditors every change with approvals and test results
- **Maintain immutable audit trail** - 7-10 year retention for regulatory compliance

**Success Criteria:**
- 80% of Standard changes auto-approved and deployed in <1 day
- 100% of Normal changes reviewed by manager/CAB within 3 business days
- Emergency changes approved by CISO + VP Engineering in <2 hours
- Zero compliance test failures in production due to proper pre-deployment verification
- Complete audit trail for all changes with immutable PostgreSQL storage

## How It Works

```
[Change Request] → [Classification Engine] → [Approval Router] → [Implementation] → [Verification] → [Audit Trail]
       ↓                    ↓                       ↓                    ↓                ↓              ↓
   FastAPI UI      Risk Assessment        CAB/Manager/CISO      Deploy + Monitor    Compliance     PostgreSQL
   React Form      (auto-detect)          (routing logic)       (state machine)      Tests         (immutable)
                                                                                        ↓
                                                                                 [Rollback Triggers]
                                                                                   - Compliance fail
                                                                                   - Metrics >20% degraded
                                                                                   - Security compromised
                                                                                   - User complaints >10/hr
                                                                                   - Audit log gaps
```

**6-Phase Workflow:**
1. **Request & Classification** - Submit change, auto-classify as Standard/Normal/Emergency
2. **Impact Assessment** - Document technical, compliance, business impact
3. **Approval** - Route to appropriate approvers based on risk level
4. **Implementation** - Execute change in controlled maintenance window
5. **Verification** - Run compliance tests, validate metrics, confirm rollback readiness
6. **Review & Close** - Post-change review, update documentation, close audit trail

## Quick Start

### 1. Clone and Setup
```bash
git clone <repo_url>
cd gcc_comp_m4_v3
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# No API keys required - this is an internal governance tool
```

### 4. Initialize Database
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; python -c "from src.l3_m4_change_management import init_database; init_database()"
```

### 5. Run Tests
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; pytest -q

# Or use script
./scripts/run_tests.ps1
```

### 6. Start API
```bash
# Windows PowerShell
$env:PYTHONPATH=$PWD; uvicorn app:app --reload

# Or use script
./scripts/run_api.ps1
```

Access the API at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 7. Explore Notebook
```bash
jupyter lab notebooks/L3_M4_Enterprise_Integration.ipynb
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./changes.db` | PostgreSQL or SQLite connection string |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `OFFLINE` | No | `false` | Run in offline mode (notebook demonstration) |

## Common Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| **Change rejected by CAB** | Insufficient impact assessment documentation | Provide detailed technical impact, compliance impact, business impact, and rollback complexity assessment |
| **Automatic rollback triggered** | Compliance tests failed post-deployment (e.g., PII detection accuracy dropped below threshold) | Review change impact on compliance controls, run compliance tests in staging first, update change request with mitigation |
| **Metrics degraded >20%** | New embedding model increased latency from 2.1s to 3.8s (81% increase) | Implement canary deployment (10% traffic), monitor for 24 hours, rollback if degradation persists |
| **Audit log gaps detected** | Log shipper crashed during deployment window, creating 37-minute gap in audit trail | Implement pre-deployment verification of logging infrastructure, add health checks for log shippers, automatic rollback on log gap detection |
| **User complaints exceed threshold** | >10 support tickets/hour about incorrect results after embedding model upgrade | Set complaint threshold alerts, implement gradual rollout, maintain user feedback monitoring dashboard |
| **Security controls compromised** | Post-deploy audit logs stopped recording due to misconfigured permissions | Verify security control functionality in staging, add automated security control tests to verification phase |
| **Emergency change lacks approval** | Critical security patch deployed without CISO sign-off due to 2-hour SLA pressure | Implement automated approval request with escalation, maintain on-call rotation for emergency approvals, document emergency process |
| **Standard change misclassified** | Routine SSL renewal flagged as Normal change, delaying deployment by 3 days | Update classification rules in system, maintain pre-approved change catalog, train team on change type criteria |
| **Rollback failed** | Cannot revert to ada-002 embeddings - snapshot not taken before deployment | Implement mandatory snapshot creation in deployment workflow, verify rollback procedure in pre-deployment checklist |
| **CAB approval delayed** | Change submitted Friday 5 PM, CAB doesn't meet until following Thursday | Schedule changes for submission Monday-Wednesday, implement SLA alerts for approval delays, escalate time-sensitive changes to Emergency |

## Decision Card

**When to use this Change Management System:**
- ✅ Operating a GCC serving multiple business units (10+ tenants)
- ✅ Processing regulated data (financial data under SOX, PII under GDPR/DPDPA)
- ✅ Subject to external audits (SOX 404, GDPR Article 32, DPDPA Section 8)
- ✅ Deploying changes that affect compliance controls (PII detection, encryption, audit logging, access controls)
- ✅ Need to demonstrate "effective internal controls over IT systems" to auditors
- ✅ Multi-stakeholder environment where changes impact Finance, Legal, Compliance, Security teams
- ✅ Require immutable audit trail with 7-10 year retention
- ✅ Need automated rollback based on compliance test failures

**When NOT to use this system:**
- ❌ Early-stage startup with <5 engineers and no regulatory requirements
- ❌ Internal tools not processing regulated data or subject to compliance
- ❌ Non-production environments (dev, staging) - use lightweight Git-based workflow
- ❌ Changes that don't affect system behavior (documentation updates, code comments)
- ❌ Single-tenant systems with no multi-stakeholder impact
- ❌ Organizations without established CAB or compliance function
- ❌ Environments where "move fast and break things" is acceptable (pre-revenue startups)
- ❌ Systems not subject to external audits

**Trade-offs:**

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Speed** | Prevents ₹2-5Cr compliance fines from unapproved changes | Standard: <1 day, Normal: 1-3 days, Emergency: <2 hours (slower than instant Git deploy) |
| **Compliance** | Audit-ready trail, automated compliance verification, immutable records | Overhead of impact assessments, CAB reviews, post-deployment verification |
| **Rollback** | Automated rollback on compliance failure, preserves compliant state | Requires snapshot creation, testing rollback procedures, maintaining rollback scripts |
| **Governance** | Multi-stakeholder approval (CAB prevents siloed decisions) | Coordination overhead, CAB meeting scheduling, approval delays |
| **Audit Trail** | 7-10 year immutable records for regulatory compliance | Database storage costs, retention management, tamper-detection overhead |
| **Risk Mitigation** | 80% reduction in production compliance incidents | Engineering effort to classify changes, document impact, wait for approvals |

**Recommended Strategy:**
- Use this system for **production systems processing regulated data**
- Use lightweight Git workflow for **dev/staging and non-regulated systems**
- Automate 80% of changes (Standard type) to minimize overhead
- Reserve CAB review for truly high-risk changes (20% of total)
- Implement canary deployments to catch issues before full rollout

## Troubleshooting

### Database Initialization Fails
If you see `OperationalError: no such table: changes`, run:
```bash
$env:PYTHONPATH=$PWD; python -c "from src.l3_m4_change_management import init_database; init_database()"
```

### Import Errors
If you see `ModuleNotFoundError: No module named 'src.l3_m4_change_management'`, ensure:
```bash
$env:PYTHONPATH=$PWD  # Windows PowerShell
```

### Tests Failing
Run tests with verbose output:
```bash
pytest -v tests/
```

### API Port Already in Use
If port 8000 is taken, specify a different port:
```bash
uvicorn app:app --reload --port 8001
```

## Architecture Details

### Change Types Classification

| Type | Risk Level | Approval Required | SLA | Examples |
|------|-----------|-------------------|-----|----------|
| **Standard** | Low | Auto-approved | <1 day | SSL certificate renewal, security patch installation, log retention config update |
| **Normal** | Medium-High | Manager or CAB | 1-3 days | Embedding model upgrade, new data source, retrieval strategy change, access control modification |
| **Emergency** | Critical | CISO + VP Engineering | <2 hours | Zero-day vulnerability patch, production outage fix, data breach mitigation |

### Rollback Triggers (Automated)

1. **Compliance Test Failure** - PII detection accuracy <98%, encryption validation failed
2. **Metrics Degraded >20%** - Latency increased >20%, error rate increased >20%
3. **Security Controls Compromised** - Audit logs stopped, access controls bypassed
4. **User Complaints >10/hour** - Support tickets indicating incorrect results
5. **Audit Log Gaps** - Missing logs during deployment window

### CAB Composition

1. **Chief Architect** - Technical feasibility, scalability
2. **Head of Security / CISO** - Security impact, vulnerability introduction
3. **Compliance Officer** - SOX, GDPR, DPDPA regulatory impact
4. **Lead DevOps Engineer** - Operational impact, rollback readiness
5. **Business Representative** - User impact, revenue risk
6. **Finance Representative** - Financial reporting accuracy (for financial data changes)
7. **Legal Representative** - Contract compliance, data residency (for data processing changes)

## Next Steps

After mastering change management:
- **GCC Compliance M4.4**: Compliance Maturity Assessment & Continuous Improvement
- **Advanced Topics**: Multi-region change coordination, automated compliance testing, AI-powered change risk prediction

## Contributing

This is an educational module from TechVoyageHub's L3 Production RAG Engineering Track. For issues or improvements, please refer to the main course repository.

## License

MIT License - See LICENSE file for details.

---

**Built with:** FastAPI, PostgreSQL, Python State Machine, Pydantic
**Compliant with:** SOX 404, GDPR Article 32, DPDPA Section 8
**Audit-ready:** 7-10 year immutable audit trail
